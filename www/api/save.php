<?php
/**
 * Nice2Know - Save API
 * Saves updated problem, solution, and asset JSONs
 * Falls back to Python if PHP has permission issues
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

debug_log("Saving data for mail_id", $mail_id);

// Convert hex mail_id to timestamp
$timestamp = find_timestamp_from_mail_id($mail_id);

if ($timestamp === null) {
    send_error('Mail ID not found: ' . $mail_id, 404);
}

debug_log("Resolved timestamp", $timestamp);

// Build file paths using timestamp
$problem_file = PROCESSED_DIR . "/{$timestamp}_problem.json";
$solution_file = PROCESSED_DIR . "/{$timestamp}_solution.json";
$asset_file = PROCESSED_DIR . "/{$timestamp}_asset.json";

// Try to save directly with PHP first
$php_save_success = try_php_save($data, $timestamp, $problem_file, $solution_file, $asset_file);

if ($php_save_success) {
    debug_log("Data saved successfully via PHP", [
        'mail_id' => $mail_id,
        'timestamp' => $timestamp
    ]);
    
    send_success([
        'mail_id' => $mail_id,
        'timestamp' => $timestamp,
        'saved_at' => date('Y-m-d H:i:s'),
        'method' => 'php',
        'files_saved' => $php_save_success
    ], 'Data saved successfully');
}

// PHP save failed - fall back to Python
debug_log("PHP save failed, trying Python fallback", $mail_id);

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
 * Try to save files using PHP
 * Returns save results on success, false on failure
 */
function try_php_save($data, $timestamp, $problem_file, $solution_file, $asset_file) {
    try {
        // Create backup directory if it doesn't exist
        $backup_dir = STORAGE_DIR . '/backups';
        if (!is_dir($backup_dir)) {
            if (!@mkdir($backup_dir, 0755, true)) {
                debug_log("Cannot create backup directory", $backup_dir);
                return false;
            }
        }
        
        // Backup existing files before overwriting
        $backup_timestamp = date('YmdHis');
        
        if (file_exists($problem_file)) {
            $backup_file = $backup_dir . "/{$timestamp}_problem_{$backup_timestamp}.json";
            if (!@copy($problem_file, $backup_file)) {
                debug_log("Warning: Failed to backup problem.json");
            }
        }
        
        if (file_exists($solution_file)) {
            $backup_file = $backup_dir . "/{$timestamp}_solution_{$backup_timestamp}.json";
            if (!@copy($solution_file, $backup_file)) {
                debug_log("Warning: Failed to backup solution.json");
            }
        }
        
        if (file_exists($asset_file)) {
            $backup_file = $backup_dir . "/{$timestamp}_asset_{$backup_timestamp}.json";
            if (!@copy($asset_file, $backup_file)) {
                debug_log("Warning: Failed to backup asset.json");
            }
        }
        
        // Save updated JSONs
        $save_results = [];
        
        // Save problem.json
        $problem_json = json_encode($data['problem'], JSON_OPTIONS);
        if ($problem_json === false) {
            debug_log("Failed to encode problem data");
            return false;
        }
        
        $bytes_written = @file_put_contents($problem_file, $problem_json);
        if ($bytes_written === false) {
            debug_log("Failed to write problem.json", $problem_file);
            return false;
        }
        $save_results['problem'] = [
            'success' => true,
            'bytes' => $bytes_written,
            'file' => basename($problem_file)
        ];
        
        // Save solution.json (if provided)
        if (!empty($data['solution'])) {
            $solution_json = json_encode($data['solution'], JSON_OPTIONS);
            if ($solution_json === false) {
                debug_log("Failed to encode solution data");
                return false;
            }
            
            $bytes_written = @file_put_contents($solution_file, $solution_json);
            if ($bytes_written === false) {
                debug_log("Failed to write solution.json", $solution_file);
                return false;
            }
            $save_results['solution'] = [
                'success' => true,
                'bytes' => $bytes_written,
                'file' => basename($solution_file)
            ];
        }
        
        // Save asset.json
        $asset_json = json_encode($data['asset'], JSON_OPTIONS);
        if ($asset_json === false) {
            debug_log("Failed to encode asset data");
            return false;
        }
        
        $bytes_written = @file_put_contents($asset_file, $asset_json);
        if ($bytes_written === false) {
            debug_log("Failed to write asset.json", $asset_file);
            return false;
        }
        $save_results['asset'] = [
            'success' => true,
            'bytes' => $bytes_written,
            'file' => basename($asset_file)
        ];
        
        return $save_results;
        
    } catch (Exception $e) {
        debug_log("PHP save exception", $e->getMessage());
        return false;
    }
}

/**
 * Save files using Python script as fallback
 */
function save_via_python($mail_id, $data) {
    // Create temp files for JSON data
    $temp_dir = sys_get_temp_dir();
    $temp_problem = $temp_dir . '/n2k_problem_' . uniqid() . '.json';
    $temp_solution = $temp_dir . '/n2k_solution_' . uniqid() . '.json';
    $temp_asset = $temp_dir . '/n2k_asset_' . uniqid() . '.json';
    
    // Write temp files
    file_put_contents($temp_problem, json_encode($data['problem'], JSON_OPTIONS));
    file_put_contents($temp_solution, json_encode($data['solution'] ?? null, JSON_OPTIONS));
    file_put_contents($temp_asset, json_encode($data['asset'], JSON_OPTIONS));
    
    // Find Python script
    $python_script = MAIL_AGENT_ROOT . '/mail_agent/utils/save_json.py';
    
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
    
    // Call Python script
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
