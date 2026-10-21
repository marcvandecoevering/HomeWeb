<?php
declare(strict_types=1);
set_error_handler(function(int $n, string $m): never { throw new RuntimeException($m); });
function fail(string $message): never { throw new RuntimeException('ThuisWeb: '.$message); }
function identity(string $key): int {
    $v = getenv($key);
    if (!preg_match('/^[1-9][0-9]{0,9}$/D', $v) || (int)$v > 2147483647) fail("$key moet een positief niet-root ID zijn");
    return (int)$v;
}
function megabytes(string $key): int {
    $v = getenv($key);
    if (!preg_match('/^([1-9][0-9]{0,5})([MG])$/D', $v, $m)) fail("$key moet bijvoorbeeld 32M of 1G zijn");
    $mb = (int)$m[1] * ($m[2] === 'G' ? 1024 : 1);
    if ($mb > 1048576) fail("$key is te groot");
    return $mb;
}
try {
    $uid = identity('PUID'); $gid = identity('PGID');
    $memory = megabytes('PHP_MEMORY_LIMIT'); $upload = megabytes('PHP_UPLOAD_LIMIT');
    $post = $upload + max(8, (int)ceil($upload * 0.1));
    if ($memory < $post) fail('PHP_MEMORY_LIMIT moet ten minste uploadlimiet plus multipart-overhead zijn');
    $tz = getenv('TZ');
    if (!in_array($tz, timezone_identifiers_list(), true) && $tz !== 'UTC') fail('TZ is geen geldige tijdzone');
    if (!is_dir('/config') || !is_readable('/config')) fail('/config is niet toegankelijk');
    if (!is_dir('/var/www/html')) fail('websitemap ontbreekt');
    $entries = array_diff(scandir('/var/www/html'), ['.', '..']);
    $marker = '/config/.thuisweb-initialized';
    if (!$entries && !file_exists($marker)) {
        // Exclusive creation refuses existing files and symlinks; no recursive ownership changes.
        $f = fopen('/var/www/html/index.html', 'x');
        $html = file_get_contents('/opt/thuisweb/index.html');
        if (fwrite($f, $html) !== strlen($html) || !fflush($f)) fail('landingpagina kon niet volledig worden geschreven');
        fclose($f);
        chown('/var/www/html/index.html', $uid); chgrp('/var/www/html/index.html', $gid);
        chmod('/var/www/html/index.html', 0644);
        chown('/var/www/html', $uid); chgrp('/var/www/html', $gid); chmod('/var/www/html', 0755);
        $fingerprint = fopen('/config/.thuisweb-landing.sha256', 'x');
        $hash = hash('sha256', $html)."\n";
        if (fwrite($fingerprint, $hash) !== strlen($hash) || !fflush($fingerprint)) fail('landingstatus kon niet worden vastgelegd');
        fclose($fingerprint);
        chmod('/config/.thuisweb-landing.sha256', 0644);
        $f = fopen($marker, 'x'); fwrite($f, "initialized\n"); fclose($f);
        echo "ThuisWeb: nieuwe landingpagina geplaatst\n";
    }
    if (!is_dir('/run/thuisweb-sessions')) mkdir('/run/thuisweb-sessions', 0700);
    chown('/run/thuisweb-sessions', $uid); chgrp('/run/thuisweb-sessions', $gid);
    $ini = "memory_limit={$memory}M\nupload_max_filesize={$upload}M\npost_max_size={$post}M\ndate.timezone=$tz\n";
    // Empty error_log sends mod_php errors through Apache's already-open stderr log.
    $ini .= "display_errors=Off\ndisplay_startup_errors=Off\nlog_errors=On\nerror_log=\nexpose_php=Off\nsession.save_path=/run/thuisweb-sessions\n";
    file_put_contents('/usr/local/etc/php/conf.d/zz-thuisweb.ini', $ini);
} catch (Throwable $e) { fwrite(STDERR, $e->getMessage()."\n"); exit(1); }
