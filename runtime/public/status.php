<?php
declare(strict_types=1);
// Only the untouched starter page opts in to publicly displaying versions.
// Replacing the page or adding index.php disables this endpoint.
$page = '/var/www/html/index.html';
$fingerprint = @file_get_contents('/config/.thuisweb-landing.sha256');
if (file_exists('/var/www/html/index.php') || !$fingerprint ||
    !is_file($page) || !is_readable($page) ||
    !hash_equals(trim($fingerprint), hash_file('sha256', $page))) {
    http_response_code(404);
    exit;
}
header('Cache-Control: no-store');
header('Content-Type: application/json; charset=utf-8');
header('X-Content-Type-Options: nosniff');
if ($_SERVER['REQUEST_METHOD'] !== 'GET') {
    header('Allow: GET');
    http_response_code(405);
    exit;
}
$opcache = function_exists('opcache_get_status') ? opcache_get_status(false) : false;
echo json_encode([
    'apache' => trim(file_get_contents('/opt/thuisweb/apache-version')),
    'php' => PHP_VERSION,
    'opcache' => phpversion('Zend OPcache') ?: null,
    'opcacheEnabled' => is_array($opcache) && ($opcache['opcache_enabled'] ?? false),
    'build' => trim(file_get_contents('/opt/thuisweb/build-revision')),
], JSON_THROW_ON_ERROR);
