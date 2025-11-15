<?php
/**
 * Nice2Know - Save API
 * Saves updated problem, solution, and asset JSONs
 *
 * POST /api/save.php
 * Body: {
 *   "mail_id": "YYYYMMDD_HHMMSS",
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
    send_error('Invalid mail_id format. Expected: YYYYMMDD_HHMMSS');
}

debug_log("Saving data for mail_id", $mail_id);

// Convert hex mail_id to timestamp if needed
$timestamp = find_timestamp_from_mail_id($mail_id);

if ($timestamp === null) {
    send_error('Mail ID not found: ' . $mail_id, 404);
}

debug_log("Resolved timestamp", $timestamp);

// Build file paths using timestamp
$problem_file = PROCESSED_DIR . "/{$timestamp}_problem.json";
$solution_file = PROCESSED_DIR . "/{$timestamp}_solution.json";
$asset_file = PROCESSED_DIR . "/{$timestamp}_asset.json";

// Create backup directory if it doesn't exist
$backup_dir = STORAGE_DIR . '/backups';
if (!is_dir($backup_dir)) {
    mkdir($backup_dir, 0755, true);
}

// Backup existing files before overwriting
$backup_timestamp = date('YmdHis');
$backup_success = true;

if (file_exists($problem_file)) {
    $backup_file = $backup_dir . "/{$mail_id}_problem_{$backup_timestamp}.json";
    if (!copy($problem_file, $backup_file)) {
        debug_log("Warning: Failed to backup problem.json");
        $backup_success = false;
    }
}

if (file_exists($solution_file)) {
    $backup_file = $backup_dir . "/{$mail_id}_solution_{$backup_timestamp}.json";
    if (!copy($solution_file, $backup_file)) {
        debug_log("Warning: Failed to backup solution.json");
        $backup_success = false;
    }
}

if (file_exists($asset_file)) {
    $backup_file = $backup_dir . "/{$mail_id}_asset_{$backup_timestamp}.json";
    if (!copy($asset_file, $backup_file)) {
        debug_log("Warning: Failed to backup asset.json");
        $backup_success = false;
    }
}

// Save updated JSONs
$save_results = [];

// Save problem.json
$problem_json = json_encode($data['problem'], JSON_OPTIONS);
if ($problem_json === false) {
    send_error('Failed to encode problem data: ' . json_last_error_msg(), 500);
}

$bytes_written = file_put_contents($problem_file, $problem_json);
if ($bytes_written === false) {
    send_error('Failed to write problem.json', 500);
}
$save_results['problem'] = [
    'success' => true,
    'bytes' => $bytes_written
];

// Save solution.json (if provided)
if (!empty($data['solution'])) {
    $solution_json = json_encode($data['solution'], JSON_OPTIONS);
    if ($solution_json === false) {
        send_error('Failed to encode solution data: ' . json_last_error_msg(), 500);
    }
    
    $bytes_written = file_put_contents($solution_file, $solution_json);
    if ($bytes_written === false) {
        send_error('Failed to write solution.json', 500);
    }
    $save_results['solution'] = [
        'success' => true,
        'bytes' => $bytes_written
    ];
}

// Save asset.json
$asset_json = json_encode($data['asset'], JSON_OPTIONS);
if ($asset_json === false) {
    send_error('Failed to encode asset data: ' . json_last_error_msg(), 500);
}

$bytes_written = file_put_contents($asset_file, $asset_json);
if ($bytes_written === false) {
    send_error('Failed to write asset.json', 500);
}
$save_results['asset'] = [
    'success' => true,
    'bytes' => $bytes_written
];

debug_log("Data saved successfully", [
    'mail_id' => $mail_id,
    'backup_created' => $backup_success,
    'results' => $save_results
]);

// Return success response
send_success([
    'mail_id' => $mail_id,
    'saved_at' => date('Y-m-d H:i:s'),
    'backup_created' => $backup_success,
    'files_saved' => $save_results
], 'Data saved successfully');
?>
