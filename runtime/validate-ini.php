<?php
declare(strict_types=1);
set_error_handler(function(int $n, string $m): never { throw new RuntimeException($m); });
try {
    $custom = parse_ini_file('/config/php.ini', true, INI_SCANNER_RAW);
    if ($custom === false) throw new RuntimeException('php.ini kan niet worden gelezen');
    $known = ini_get_all();
    $check = function(array $values) use (&$check, $known): void {
        foreach ($values as $key => $value) {
            if (is_array($value)) { $check($value); continue; }
            if (!array_key_exists($key, $known) && !in_array($key, ['extension','zend_extension'], true)) {
                throw new RuntimeException("onbekende php.ini-instelling: $key");
            }
        }
    };
    $check($custom);
} catch (Throwable $e) {
    fwrite(STDERR, 'ThuisWeb: ongeldige /config/php.ini: '.$e->getMessage()."\n"); exit(1);
}
