<?php
/**
 * Nice2Know - Save API (Export Strategy)
 * Saves edited data to separate export/ directory
 * Original files in processed/ remain untouched
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

debug_log("Saving edited data for mail_id", $mail_id);

// Convert hex mail_id to timestamp
$timestamp = find_timestamp_from_mail_id($mail_id);

if ($timestamp === null) {
    send_error('Mail ID not found: ' . $mail_id, 404);
}

debug_log("Resolved timestamp", $timestamp);

// Export directory
$export_dir = STORAGE_DIR . '/export';

// Create export directory if it doesn't exist
if (!is_dir($export_dir)) {
    if (!mkdir($export_dir, 0775, true)) {
        send_error('Failed to create export directory', 500);
    }
}

// Build consolidated export file
$export_file = $export_dir . "/{$timestamp}_edited.json";

// Create consolidated structure
$export_data = [
    'mail_id' => $mail_id,
    'timestamp' => $timestamp,
    'edited_at' => date('Y-m-d H:i:s'),
    'problem' => $data['problem'],
    'solution' => $data['solution'] ?? null,
    'asset' => $data['asset']
];

// Save to export directory
$json_output = json_encode($export_data, JSON_OPTIONS);
if ($json_output === false) {
    send_error('Failed to encode export data: ' . json_last_error_msg(), 500);
}

$bytes_written = file_put_contents($export_file, $json_output);
if ($bytes_written === false) {
    send_error('Failed to write export file', 500);
}

debug_log("Exported edited data", [
    'file' => basename($export_file),
    'bytes' => $bytes_written
]);

// Return success response
send_success([
    'mail_id' => $mail_id,
    'timestamp' => $timestamp,
    'saved_at' => date('Y-m-d H:i:s'),
    'export_file' => basename($export_file),
    'bytes' => $bytes_written
], 'Data exported successfully');
?>
