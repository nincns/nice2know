<?php
/**
 * Nice2Know - Load API
 * Loads problem, solution, and asset JSONs for a given mail_id
 * Prioritizes edited exports over processed files
 *
 * GET /api/load.php?mail_id=575496876c3645bc8bf5f79c1696c134
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

// Convert hex mail_id to timestamp if needed
$timestamp = find_timestamp_from_mail_id($mail_id);

if ($timestamp === null) {
    send_error('Mail ID not found: ' . $mail_id, 404);
}

debug_log("Resolved timestamp", $timestamp);

// Check if edited export exists (has priority over processed files)
$export_dir = STORAGE_DIR . '/export';
$export_file = $export_dir . "/{$timestamp}_edited.json";
$has_export = file_exists($export_file);

if ($has_export) {
    debug_log("Loading from export (edited version)", $export_file);
    
    // Load consolidated export file
    $export_content = file_get_contents($export_file);
    $export_data = json_decode($export_content, true);
    
    if (json_last_error() !== JSON_ERROR_NONE) {
        debug_log("Failed to parse export file, falling back to processed files");
        $has_export = false;
    } else {
        // Return edited data from export
        $data = [
            'problem' => $export_data['problem'],
            'solution' => $export_data['solution'] ?? null,
            'asset' => $export_data['asset'],
            'metadata' => [
                'mail_id' => $mail_id,
                'loaded_at' => date('Y-m-d H:i:s'),
                'source' => 'export',
                'edited_at' => $export_data['edited_at'] ?? null,
                'files' => [
                    'problem' => true,
                    'solution' => isset($export_data['solution']),
                    'asset' => true
                ]
            ]
        ];
        
        debug_log("Data loaded from export", [
            'mail_id' => $mail_id,
            'edited_at' => $export_data['edited_at'] ?? 'unknown'
        ]);
        
        send_success($data);
    }
}

// No export or export failed - load from processed files
debug_log("Loading from processed files (original version)");

// Build file paths using timestamp
$problem_file = PROCESSED_DIR . "/{$timestamp}_problem.json";
$solution_file = PROCESSED_DIR . "/{$timestamp}_solution.json";
$asset_file = PROCESSED_DIR . "/{$timestamp}_asset.json";

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
    'source' => 'processed',
    'files' => $files_status
];

debug_log("Data loaded successfully from processed", [
    'mail_id' => $mail_id,
    'has_solution' => $data['solution'] !== null
]);

// Return success response
send_success($data);
?>
