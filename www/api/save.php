<?php
/**
 * Nice2Know - Save API (Python-Only)
 * Always uses Python to save files (no PHP write attempts)
 *
 * POST /api/save.php
 * Body: {
 *   "mail_id": "575496876c3645bc8bf5f79c1696c134",
 *   "problem": {...},
 *   "solution": {...},
 *   "asset": {...}
 * }
 */

require_once '../config.php';

// Handle CORS preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    header('Access-Control-Allow-Origin: ' . ALLOWED_ORIGINS);
    header('Access-Control-Allow-Methods: POST, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type');
    http_response_code(200);
    exit;
}

// Only allow POST requests
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    send_error('Method not allowed. Use POST.', 405);
}

// Get JSON input
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    send_error('Invalid JSON: ' . json_last_error_msg());
}

// Validate required fields
if (empty($data['mail_id'])) {
    send_error('Missing required field: mail_id');
}

if (empty($data['problem'])) {
    send_error('Missing required field: problem');
}

if (empty($data['asset'])) {
    send_error('Missing required field: asset');
}

// Sanitize and validate mail_id
$mail_id = sanitize_mail_id($data['mail_id']);

if (!validate_mail_id($mail_id)) {
    send_error('Invalid mail_id format');
}

debug_log("Saving data via Python for mail_id", $mail_id);

// Convert hex mail_id to timestamp (for response info)
$timestamp = find_timestamp_from_mail_id($mail_id);

if ($timestamp === null) {
    send_error('Mail ID not found: ' . $mail_id, 404);
}

// Save via Python (always, no PHP write attempt)
$python_result = save_via_python($mail_id, $data);

if ($python_result['success']) {
    send_success([
        'mail_id' => $mail_id,
        'timestamp' => $timestamp,
        'saved_at' => date('Y-m-d H:i:s'),
        'method' => 'python',
        'output' => $python_result['output']
    ], 'Data saved successfully via Python');
} else {
    send_error('Failed to save: ' . $python_result['error'], 500);
}

/**
 * Save files using Python script
 */
function save_via_python($mail_id, $data) {
    // Create temp files for JSON data
    $temp_dir = sys_get_temp_dir();
    $temp_problem = $temp_dir . '/n2k_problem_' . uniqid() . '.json';
    $temp_solution = $temp_dir . '/n2k_solution_' . uniqid() . '.json';
    $temp_asset = $temp_dir . '/n2k_asset_' . uniqid() . '.json';
    
    // Write temp files (PHP can write to /tmp)
    file_put_contents($temp_problem, json_encode($data['problem'], JSON_OPTIONS));
    file_put_contents($temp_solution, json_encode($data['solution'] ?? null, JSON_OPTIONS));
    file_put_contents($temp_asset, json_encode($data['asset'], JSON_OPTIONS));
    
    // Path to Python script
    $python_script = MAIL_AGENT_ROOT . '/utils/save_json.py';
    
    if (!file_exists($python_script)) {
        // Cleanup temp files
        @unlink($temp_problem);
        @unlink($temp_solution);
        @unlink($temp_asset);
        
        return [
            'success' => false,
            'error' => 'Python save script not found: ' . $python_script
        ];
    }
    
    // Determine which Python to use
    // Try to use the venv Python if available
    $python_paths = [
        '/opt/nice2know/venv/bin/python3',  // venv
        '/usr/bin/python3',                  // system
        'python3'                            // PATH
    ];
    
    $python_cmd = 'python3';
    foreach ($python_paths as $path) {
        if (file_exists($path)) {
            $python_cmd = $path;
            break;
        }
    }
    
    // Build command
    $cmd = sprintf(
        '%s %s %s %s %s %s 2>&1',
        escapeshellarg($python_cmd),
        escapeshellarg($python_script),
        escapeshellarg($mail_id),
        escapeshellarg($temp_problem),
        escapeshellarg($temp_solution),
        escapeshellarg($temp_asset)
    );
    
    debug_log("Executing Python command", $cmd);
    
    $output = [];
    $return_code = 0;
    exec($cmd, $output, $return_code);
    
    // Cleanup temp files
    @unlink($temp_problem);
    @unlink($temp_solution);
    @unlink($temp_asset);
    
    if ($return_code !== 0) {
        $error_msg = implode("\n", $output);
        debug_log("Python save failed", $error_msg);
        return [
            'success' => false,
            'error' => $error_msg
        ];
    }
    
    return [
        'success' => true,
        'output' => $output
    ];
}
?>
