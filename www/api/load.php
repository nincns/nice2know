<?php
/**
 * Nice2Know - Load API
 * Loads problem, solution, and asset JSONs for a given mail_id
 *
 * GET /api/load.php?mail_id=YYYYMMDD_HHMMSS
 */

require_once '../config.php';

// Handle CORS preflight
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    header('Access-Control-Allow-Origin: ' . ALLOWED_ORIGINS);
    header('Access-Control-Allow-Methods: GET, OPTIONS');
    header('Access-Control-Allow-Headers: Content-Type');
    http_response_code(200);
    exit;
}

// Only allow GET requests
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    send_error('Method not allowed. Use GET.', 405);
}

// Get and validate mail_id parameter
$mail_id = $_GET['mail_id'] ?? null;

if (empty($mail_id)) {
    send_error('Missing required parameter: mail_id');
}

// Sanitize and validate mail_id
$mail_id = sanitize_mail_id($mail_id);

if (!validate_mail_id($mail_id)) {
    send_error('Invalid mail_id format. Expected: YYYYMMDD_HHMMSS');
}

debug_log("Loading data for mail_id", $mail_id);

// Build file paths
$problem_file = PROCESSED_DIR . "/{$mail_id}_problem.json";
$solution_file = PROCESSED_DIR . "/{$mail_id}_solution.json";
$asset_file = PROCESSED_DIR . "/{$mail_id}_asset.json";

// Check if files exist
$files_status = [
    'problem' => file_exists($problem_file),
    'solution' => file_exists($solution_file),
    'asset' => file_exists($asset_file)
];

debug_log("Files status", $files_status);

if (!$files_status['problem']) {
    send_error('Problem file not found for mail_id: ' . $mail_id, 404);
}

if (!$files_status['asset']) {
    send_error('Asset file not found for mail_id: ' . $mail_id, 404);
}

// Load JSON files
$data = [];

// Load problem.json (required)
$problem_content = file_get_contents($problem_file);
$data['problem'] = json_decode($problem_content, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    send_error('Failed to parse problem.json: ' . json_last_error_msg(), 500);
}

// Load solution.json (optional - might not exist for all cases)
if ($files_status['solution']) {
    $solution_content = file_get_contents($solution_file);
    $data['solution'] = json_decode($solution_content, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        debug_log("Warning: Failed to parse solution.json", json_last_error_msg());
        $data['solution'] = null;
    }
} else {
    $data['solution'] = null;
}

// Load asset.json (required)
$asset_content = file_get_contents($asset_file);
$data['asset'] = json_decode($asset_content, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    send_error('Failed to parse asset.json: ' . json_last_error_msg(), 500);
}

// Add metadata
$data['metadata'] = [
    'mail_id' => $mail_id,
    'loaded_at' => date('Y-m-d H:i:s'),
    'files' => $files_status
];

debug_log("Data loaded successfully", [
    'mail_id' => $mail_id,
    'has_solution' => $data['solution'] !== null
]);

// Return success response
send_success($data);
?>
