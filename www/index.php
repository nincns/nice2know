<?php
/**
 * Nice2Know - Web Editor Entry Point
 * Main router for the web editor
 */

require_once 'config.php';

// Get mail_id from URL parameter
$mail_id = $_GET['mail_id'] ?? null;

// If no mail_id provided, show error or list
if (empty($mail_id)) {
    ?>
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title><?php echo APP_NAME; ?> - Error</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 600px;
                margin: 100px auto;
                padding: 20px;
                text-align: center;
            }
            .error-box {
                background: #fee;
                border: 2px solid #c33;
                border-radius: 8px;
                padding: 30px;
                color: #c33;
            }
            h1 { margin: 0 0 10px 0; }
            p { margin: 10px 0; color: #666; }
            code {
                background: #f5f5f5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="error-box">
            <h1>⚠️ Mail-ID fehlt</h1>
            <p>Bitte rufen Sie diese Seite mit einer gültigen Mail-ID auf:</p>
            <p><code>?mail_id=YYYYMMDD_HHMMSS</code></p>
        </div>
    </body>
    </html>
    <?php
    exit;
}

// Sanitize and validate mail_id
$mail_id = sanitize_mail_id($mail_id);

if (!validate_mail_id($mail_id)) {
    ?>
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title><?php echo APP_NAME; ?> - Invalid Mail-ID</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 600px;
                margin: 100px auto;
                padding: 20px;
                text-align: center;
            }
            .error-box {
                background: #fee;
                border: 2px solid #c33;
                border-radius: 8px;
                padding: 30px;
                color: #c33;
            }
            h1 { margin: 0 0 10px 0; }
            p { margin: 10px 0; color: #666; }
            code {
                background: #f5f5f5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="error-box">
            <h1>⚠️ Ungültige Mail-ID</h1>
            <p>Die Mail-ID hat ein ungültiges Format.</p>
            <p>Erwartet: <code>YYYYMMDD_HHMMSS</code> oder <code>32-stellige Hex-ID</code></p>
            <p>Erhalten: <code><?php echo htmlspecialchars($mail_id); ?></code></p>
        </div>
    </body>
    </html>
    <?php
    exit;
}

// Check if files exist
$timestamp = find_timestamp_from_mail_id($mail_id);

if ($timestamp === null) {
    ?>
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title><?php echo APP_NAME; ?> - Not Found</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 600px;
                margin: 100px auto;
                padding: 20px;
                text-align: center;
            }
            .error-box {
                background: #fef9e7;
                border: 2px solid #f39c12;
                border-radius: 8px;
                padding: 30px;
                color: #d68910;
            }
            h1 { margin: 0 0 10px 0; }
            p { margin: 10px 0; color: #666; }
            code {
                background: #f5f5f5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="error-box">
            <h1>📭 Daten nicht gefunden</h1>
            <p>Für die Mail-ID <code><?php echo htmlspecialchars($mail_id); ?></code> wurden keine Daten gefunden.</p>
            <p>Möglicherweise wurde diese Mail noch nicht verarbeitet oder die ID ist falsch.</p>
        </div>
    </body>
    </html>
    <?php
    exit;
}

$problem_file = PROCESSED_DIR . "/{$timestamp}_problem.json";
$asset_file = PROCESSED_DIR . "/{$timestamp}_asset.json";

if (!file_exists($problem_file) || !file_exists($asset_file)) {
    ?>
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title><?php echo APP_NAME; ?> - Not Found</title>
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                max-width: 600px;
                margin: 100px auto;
                padding: 20px;
                text-align: center;
            }
            .error-box {
                background: #fef9e7;
                border: 2px solid #f39c12;
                border-radius: 8px;
                padding: 30px;
                color: #d68910;
            }
            h1 { margin: 0 0 10px 0; }
            p { margin: 10px 0; color: #666; }
            code {
                background: #f5f5f5;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
        </style>
    </head>
    <body>
        <div class="error-box">
            <h1>📭 Daten nicht gefunden</h1>
            <p>Für die Mail-ID <code><?php echo htmlspecialchars($mail_id); ?></code> wurden keine Daten gefunden.</p>
            <p>Möglicherweise wurde diese Mail noch nicht verarbeitet oder die ID ist falsch.</p>
        </div>
    </body>
    </html>
    <?php
    exit;
}

// All checks passed - load the editor
debug_log("Loading editor for mail_id", $mail_id);
?>
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo APP_NAME; ?> - <?php echo htmlspecialchars($mail_id); ?></title>
    <link rel="stylesheet" href="static/css/editor.css">
</head>
<body>
    <div id="app" data-mail-id="<?php echo htmlspecialchars($mail_id); ?>">
        <div class="loading">
            <div class="spinner"></div>
            <p>Lade Daten...</p>
        </div>
    </div>
    
    <script src="static/js/api.js"></script>
    <script src="static/js/editor.js"></script>
</body>
</html>
<?php
debug_log("Editor HTML served", $mail_id);
?>
