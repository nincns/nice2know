<?php
/**
 * Nice2Know - Save API (Python Proxy)
 * Calls Python script to save files (workaround for permission issues)
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

// Sanitize mail_id
$mail_id = sanitize_mail_id($data['mail_id']);

if (!validate_mail_id($mail_id)) {
    send_error('Invalid mail_id format');
}

debug_log("Saving via Python for mail_id", $mail_id);

// Create temp files for JSON data
$temp_dir = sys_get_temp_dir();
$temp_problem = $temp_dir . '/problem_' . uniqid() . '.json';
$temp_solution = $temp_dir . '/solution_' . uniqid() . '.json';
$temp_asset = $temp_dir . '/asset_' . uniqid() . '.json';

// Write temp files
file_put_contents($temp_problem, json_encode($data['problem'], JSON_OPTIONS));
file_put_contents($temp_solution, json_encode($data['solution'] ?? null, JSON_OPTIONS));
file_put_contents($temp_asset, json_encode($data['asset'], JSON_OPTIONS));

// Call Python script
$python_script = MAIL_AGENT_ROOT . '/mail_agent/utils/save_json.py';
$cmd = sprintf(
    'python3 %s %s %s %s %s 2>&1',
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
unlink($temp_problem);
unlink($temp_solution);
unlink($temp_asset);

if ($return_code !== 0) {
    $error_msg = implode("\n", $output);
    debug_log("Python save failed", $error_msg);
    send_error('Failed to save via Python: ' . $error_msg, 500);
}

debug_log("Python save successful", implode("\n", $output));

// Return success response
send_success([
    'mail_id' => $mail_id,
    'saved_at' => date('Y-m-d H:i:s'),
    'method' => 'python',
    'output' => $output
], 'Data saved successfully via Python');
?>
