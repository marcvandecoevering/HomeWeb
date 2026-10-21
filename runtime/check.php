<?php
declare(strict_types=1);
$policy = json_decode(file_get_contents('/opt/thuisweb/security-policy.json'), true, flags: JSON_THROW_ON_ERROR);
if (PHP_MAJOR_VERSION !== 8 || PHP_MINOR_VERSION !== 3 || version_compare(PHP_VERSION, $policy['minimum'], '<')) {
    fwrite(STDERR, "ThuisWeb: geblokkeerde PHP-versie " . PHP_VERSION . "\n"); exit(1);
}
$required = ['curl','mbstring','intl','gd','zip','xml','dom','Zend OPcache','mysqli','pdo_mysql','pgsql','pdo_pgsql','pdo_sqlite','sqlite3','session','fileinfo','posix'];
foreach ($required as $extension) {
    if (!extension_loaded($extension)) { fwrite(STDERR, "ThuisWeb: extensie ontbreekt: $extension\n"); exit(1); }
}
$gd = gd_info();
if (!$gd['JPEG Support'] || !$gd['FreeType Support']) { fwrite(STDERR, "ThuisWeb: GD mist JPEG/FreeType\n"); exit(1); }
echo PHP_VERSION, "\n";
