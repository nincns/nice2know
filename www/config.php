<?php
/**
 * Nice2Know - Web Editor Configuration
 * Central configuration file for all PHP scripts
 */

// Error reporting for development
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Auto-detect mail_agent root directory
function find_mail_agent_root($start_path) {
    $current = realpath($start_path);
    for ($i = 0; $i < 5; $i++) {
        if (is_dir("$current/agents") &&
            is_dir("$current/catalog") &&
            is_dir("$current/storage")) {
            return $current;
        }
        $parent = dirname($current);
        if ($parent === $current) break;
        $current = $parent;
    }
    return $start_path;
}

// Load application configuration from JSON
function load_application_config($mail_agent_root) {
    $config_file = $mail_agent_root . '/config/connections/application.json';
    
    if (!file_exists($config_file)) {
        error_log("application.json not found at: $config_file");
        return null;
    }
    
    $json = file_get_contents($config_file);
    $config = json_decode($json, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        error_log("Error parsing application.json: " . json_last_error_msg());
        return null;
    }
    
    return $config;
}

// Detect mail_agent root from current script location
$detected_root = find_mail_agent_root(__DIR__);

// Load config
$app_config = load_application_config($detected_root);

if ($app_config === null) {
    die("FATAL: Could not load application.json configuration");
}

// Define base paths from config
define('MAIL_AGENT_ROOT', $detected_root);

// Get storage base path from config (default to ./storage if not found)
$storage_base_path = $app_config['storage']['base_path'] ?? './storage';

// Resolve relative path
if (substr($storage_base_path, 0, 1) !== '/') {
    // Relative path - resolve from MAIL_AGENT_ROOT
    $storage_base_path = MAIL_AGENT_ROOT . '/' . $storage_base_path;
}

define('STORAGE_DIR', realpath($storage_base_path) ?: $storage_base_path);
define('PROCESSED_DIR', STORAGE_DIR . '/processed');
define('SENT_DIR', STORAGE_DIR . '/sent');
define('MAILS_DIR', STORAGE_DIR . '/mails');

// Application settings from config
define('APP_NAME', $app_config['app_name'] ?? 'Nice2Know Editor');
define('APP_VERSION', $app_config['version'] ?? '1.0.0');
define('DEBUG_MODE', true); // Set to false in production

// Web server settings - load from config if available
$base_url = $app_config['base_url'] ?? 'http://10.147.17.50/n2k';
define('BASE_URL', $base_url);
define('EDITOR_PATH', '/');

// API settings
define('API_RESPONSE_TYPE', 'application/json');
define('ALLOWED_ORIGINS', '*'); // TODO: Restrict in production

// File settings
define('JSON_OPTIONS', JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);

// Verify critical directories exist
function verify_directories() {
    $required_dirs = [
        MAIL_AGENT_ROOT => 'Mail Agent Root',
        STORAGE_DIR => 'Storage Directory',
        PROCESSED_DIR => 'Processed Directory'
    ];
    
    $errors = [];
    foreach ($required_dirs as $dir => $name) {
        if (!is_dir($dir)) {
            $errors[] = "$name not found: $dir";
        }
    }
    
    return $errors;
}

// Helper function: Send JSON response
function send_json_response($data, $status_code = 200) {
    http_response_code($status_code);
    header('Content-Type: ' . API_RESPONSE_TYPE);
    header('Access-Control-Allow-Origin: ' . ALLOWED_ORIGINS);
    echo json_encode($data, JSON_OPTIONS);
    exit;
}

// Helper function: Send error response
function send_error($message, $status_code = 400, $details = null) {
    $response = [
        'success' => false,
        'error' => $message
    ];
    if (DEBUG_MODE && $details) {
        $response['details'] = $details;
    }
    send_json_response($response, $status_code);
}

// Helper function: Send success response
function send_success($data = null, $message = null) {
    $response = ['success' => true];
    if ($message) {
        $response['message'] = $message;
    }
    if ($data !== null) {
        $response['data'] = $data;
    }
    send_json_response($response, 200);
}

// Helper function: Validate mail_id format
function validate_mail_id($mail_id) {
    // Accept both formats:
    // 1. Timestamp format: YYYYMMDD_HHMMSS (legacy)
    // 2. Hex format: 32 hex characters (current)
    if (preg_match('/^[0-9]{8}_[0-9]{6}$/', $mail_id)) {
        return true; // Legacy timestamp format
    }
    if (preg_match('/^[a-f0-9]{32}$/', $mail_id)) {
        return true; // Hex format
    }
    return false;
}

// Debug output in development mode
if (DEBUG_MODE) {
    error_log("Nice2Know Config Loaded:");
    error_log("  MAIL_AGENT_ROOT: " . MAIL_AGENT_ROOT);
    error_log("  STORAGE_DIR: " . STORAGE_DIR);
    error_log("  BASE_URL: " . BASE_URL);
}
?>
