sudo tee /opt/nice2know/www/config.php > /dev/null << 'EOF'
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

// Define base paths - HARDCODED for www/ directory
define('MAIL_AGENT_ROOT', '/opt/nice2know/mail_agent');
define('STORAGE_DIR', MAIL_AGENT_ROOT . '/storage');
define('PROCESSED_DIR', STORAGE_DIR . '/processed');
define('SENT_DIR', STORAGE_DIR . '/sent');
define('MAILS_DIR', STORAGE_DIR . '/mails');

// Application settings
define('APP_NAME', 'Nice2Know Editor');
define('APP_VERSION', '1.0.0');
define('DEBUG_MODE', true); // Set to false in production

// Web server settings
define('BASE_URL', 'http://10.147.17.50/n2k');
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
    // 2. Hex mail ID: 32 hex characters (from JSON)
    if (preg_match('/^\d{8}_\d{6}$/', $mail_id)) {
        return true; // Timestamp format
    }
    if (preg_match('/^[a-f0-9]{32}$/', $mail_id)) {
        return true; // Hex mail ID
    }
    return false;
}

// Helper function: Sanitize mail_id (prevent path traversal)
function sanitize_mail_id($mail_id) {
    // Remove any path separators and only allow alphanumeric + underscore
    return preg_replace('/[^a-zA-Z0-9_]/', '', $mail_id);
}

// Helper function: Generate editor URL for a given mail_id
function get_editor_url($mail_id) {
    $sanitized_id = sanitize_mail_id($mail_id);
    return BASE_URL . EDITOR_PATH . '?mail_id=' . urlencode($sanitized_id);
}

// Helper function: Generate confirmation URL for a given mail_id
function get_confirm_url($mail_id) {
    $sanitized_id = sanitize_mail_id($mail_id);
    return BASE_URL . '/confirm.php?mail_id=' . urlencode($sanitized_id);
}

// Helper function: Find timestamp from hex mail_id by searching JSON files
function find_timestamp_from_mail_id($mail_id) {
    // If it's already a timestamp, return it
    if (preg_match('/^\d{8}_\d{6}$/', $mail_id)) {
        return $mail_id;
    }
    
    // Search for the mail_id in problem.json files
    $files = glob(PROCESSED_DIR . '/*_problem.json');
    
    foreach ($files as $file) {
        $content = file_get_contents($file);
        $data = json_decode($content, true);
        
        if (isset($data['mail_id']) && $data['mail_id'] === $mail_id) {
            // Extract timestamp from filename
            $basename = basename($file, '_problem.json');
            return $basename;
        }
    }
    
    return null; // Not found
}

// Log function for debugging
function debug_log($message, $data = null) {
    if (!DEBUG_MODE) return;
    
    $log_entry = "[" . date('Y-m-d H:i:s') . "] " . $message;
    if ($data !== null) {
        $log_entry .= " | Data: " . json_encode($data);
    }
    error_log($log_entry);
}

// Verify directories on config load
if (DEBUG_MODE) {
    $dir_errors = verify_directories();
    if (!empty($dir_errors)) {
        debug_log("Directory verification failed", $dir_errors);
    } else {
        debug_log("Config loaded successfully", [
            'root' => MAIL_AGENT_ROOT,
            'storage' => STORAGE_DIR,
            'processed' => PROCESSED_DIR
        ]);
    }
}
?>
EOF

# Berechtigungen setzen
sudo chown www-data:www-data /opt/nice2know/www/config.php
sudo chmod 644 /opt/nice2know/www/config.php

# Testen
php -r "
require '/opt/nice2know/www/config.php';
echo 'Valid timestamp: ' . (validate_mail_id('20251115_222216') ? 'YES' : 'NO') . PHP_EOL;
echo 'Valid hex: ' . (validate_mail_id('575496876c3645bc8bf5f79c1696c134') ? 'YES' : 'NO') . PHP_EOL;
"
