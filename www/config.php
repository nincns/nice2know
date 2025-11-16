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
    
    // Try up to 5 levels up
    for ($i = 0; $i < 5; $i++) {
        // Check for key directories that identify mail_agent root
        if (is_dir("$current/agents") &&
            is_dir("$current/catalog") &&
            is_dir("$current/config")) {
            return $current;
        }
        
        $parent = dirname($current);
        if ($parent === $current) break; // Reached filesystem root
        $current = $parent;
    }
    
    // Fallback: Try common locations
    $common_paths = [
        '/opt/nice2know/mail_agent',
        dirname(__DIR__), // Parent of www/
        __DIR__ . '/../mail_agent'
    ];
    
    foreach ($common_paths as $path) {
        $resolved = realpath($path);
        if ($resolved && is_dir("$resolved/config")) {
            return $resolved;
        }
    }
    
    return null;
}

// Detect mail_agent root from current script location
$detected_root = find_mail_agent_root(__DIR__);

if ($detected_root === null) {
    // Last resort: check if we're inside mail_agent already
    if (is_dir(__DIR__ . '/config') && is_dir(__DIR__ . '/agents')) {
        $detected_root = __DIR__;
    } else {
        error_log("FATAL: Could not detect mail_agent root directory");
        error_log("Started from: " . __DIR__);
        die("FATAL: Could not detect mail_agent root directory. Please check installation.");
    }
}

// Load application configuration from JSON
function load_application_config($mail_agent_root) {
    $config_file = $mail_agent_root . '/config/connections/application.json';
    
    if (!file_exists($config_file)) {
        error_log("application.json not found at: $config_file");
        error_log("mail_agent_root: $mail_agent_root");
        error_log("Directory contents: " . print_r(scandir($mail_agent_root), true));
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

// Load config
$app_config = load_application_config($detected_root);

if ($app_config === null) {
    error_log("FATAL: Could not load application.json from: $detected_root");
    die("FATAL: Could not load application.json configuration<br>Root: $detected_root<br>Expected: $detected_root/config/connections/application.json");
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

// ============================================================================
// HELPER FUNCTIONS
// ============================================================================

// Debug logging function
function debug_log($message, $data = null) {
    if (!DEBUG_MODE) {
        return;
    }
    
    $log_message = "[DEBUG] $message";
    
    if ($data !== null) {
        if (is_array($data) || is_object($data)) {
            $log_message .= ": " . print_r($data, true);
        } else {
            $log_message .= ": " . $data;
        }
    }
    
    error_log($log_message);
}

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

// Send JSON response
function send_json_response($data, $status_code = 200) {
    http_response_code($status_code);
    header('Content-Type: ' . API_RESPONSE_TYPE);
    header('Access-Control-Allow-Origin: ' . ALLOWED_ORIGINS);
    echo json_encode($data, JSON_OPTIONS);
    exit;
}

// Send error response
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

// Send success response
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

// Validate mail_id format
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

// Sanitize mail_id (remove dangerous characters)
function sanitize_mail_id($mail_id) {
    // Remove everything except alphanumeric and underscore
    $sanitized = preg_replace('/[^a-zA-Z0-9_]/', '', $mail_id);
    
    // Limit length to prevent issues
    $sanitized = substr($sanitized, 0, 64);
    
    return $sanitized;
}

// Get safe mail_id from request
function get_safe_mail_id($param_name = 'mail_id') {
    $mail_id = $_GET[$param_name] ?? $_POST[$param_name] ?? null;
    
    if ($mail_id === null) {
        return null;
    }
    
    // Sanitize first
    $mail_id = sanitize_mail_id($mail_id);
    
    // Then validate
    if (!validate_mail_id($mail_id)) {
        return null;
    }
    
    return $mail_id;
}

// Find timestamp from mail_id by searching in processed directory
function find_timestamp_from_mail_id($mail_id) {
    // Search for files matching the mail_id in processed directory
    $pattern = PROCESSED_DIR . '/*_problem.json';
    $problem_files = glob($pattern);
    
    if (empty($problem_files)) {
        error_log("No problem files found in: " . PROCESSED_DIR);
        return null;
    }
    
    // Search through all problem.json files
    foreach ($problem_files as $file) {
        $json_content = file_get_contents($file);
        $data = json_decode($json_content, true);
        
        if ($data && isset($data['mail_id']) && $data['mail_id'] === $mail_id) {
            // Extract timestamp from filename
            // Format: YYYYMMDD_HHMMSS_problem.json
            $filename = basename($file);
            if (preg_match('/^(\d{8}_\d{6})_problem\.json$/', $filename, $matches)) {
                debug_log("Found timestamp for mail_id", $mail_id . " → " . $matches[1]);
                return $matches[1];
            }
        }
    }
    
    error_log("No timestamp found for mail_id: $mail_id");
    return null;
}

// Load JSON file safely
function load_json_file($filepath) {
    if (!file_exists($filepath)) {
        error_log("JSON file not found: $filepath");
        return null;
    }
    
    $json_content = file_get_contents($filepath);
    $data = json_decode($json_content, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        error_log("Error parsing JSON from $filepath: " . json_last_error_msg());
        return null;
    }
    
    return $data;
}

// Get all JSON files for a timestamp
function get_json_files_for_timestamp($timestamp) {
    $files = [
        'problem' => PROCESSED_DIR . "/{$timestamp}_problem.json",
        'solution' => PROCESSED_DIR . "/{$timestamp}_solution.json",
        'asset' => PROCESSED_DIR . "/{$timestamp}_asset.json"
    ];
    
    $result = [];
    foreach ($files as $type => $filepath) {
        if (file_exists($filepath)) {
            $result[$type] = $filepath;
        } else {
            debug_log("Warning: $type file not found", $filepath);
        }
    }
    
    return $result;
}

// Load all JSONs for a mail_id
function load_data_by_mail_id($mail_id) {
    debug_log("Loading data for mail_id", $mail_id);
    
    // Find timestamp
    $timestamp = find_timestamp_from_mail_id($mail_id);
    
    if (!$timestamp) {
        debug_log("Timestamp not found for mail_id", $mail_id);
        return null;
    }
    
    // Get file paths
    $files = get_json_files_for_timestamp($timestamp);
    
    if (empty($files)) {
        error_log("No JSON files found for timestamp: $timestamp");
        return null;
    }
    
    debug_log("Found JSON files", array_keys($files));
    
    // Load all files
    $data = [
        'timestamp' => $timestamp,
        'mail_id' => $mail_id
    ];
    
    foreach ($files as $type => $filepath) {
        $json_data = load_json_file($filepath);
        if ($json_data) {
            $data[$type] = $json_data;
        }
    }
    
    // Ensure we have at least problem data
    if (!isset($data['problem'])) {
        error_log("Problem data not found for mail_id: $mail_id");
        return null;
    }
    
    debug_log("Successfully loaded data", array_keys($data));
    return $data;
}

// ============================================================================
// DEBUG OUTPUT
// ============================================================================

if (DEBUG_MODE) {
    error_log("=== Nice2Know Config Loaded ===");
    error_log("MAIL_AGENT_ROOT: " . MAIL_AGENT_ROOT);
    error_log("STORAGE_DIR: " . STORAGE_DIR);
    error_log("PROCESSED_DIR: " . PROCESSED_DIR);
    error_log("BASE_URL: " . BASE_URL);
    error_log("Config file: " . MAIL_AGENT_ROOT . '/config/connections/application.json');
    
    // Verify directories
    $errors = verify_directories();
    if (!empty($errors)) {
        error_log("WARNING: Directory verification failed:");
        foreach ($errors as $error) {
            error_log("  - $error");
        }
    }
}
?>
