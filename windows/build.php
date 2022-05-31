<?php

declare(strict_types=1);

define('PYTHON_VERSION', '3.10.4');
define('PYTHON_X32_URL', 'https://www.python.org/ftp/python/' . PYTHON_VERSION . '/python-' . PYTHON_VERSION . '-embed-win32.zip');
define('PYTHON_X64_URL', 'https://www.python.org/ftp/python/' . PYTHON_VERSION . '/python-' . PYTHON_VERSION . '-embed-amd64.zip');
define('GET_PIP_URL', 'https://bootstrap.pypa.io/get-pip.py');
define('AGENT_INI_URL', 'https://monitoring.platform360.io/agent360-windows.ini');
define('NSSM_URL', 'https://nssm.cc/release/nssm-2.24.zip');

define('BASE_DIR', dirname(__DIR__));
define('WIN_DIR', BASE_DIR . '/windows');
define('BUILD_DIR', WIN_DIR . '/build');
define('DIST_DIR', WIN_DIR . '/dist');
define('TMP_DIR', WIN_DIR . '/tmp');

function rrmdir(string $dir): void
{
    $names = scandir($dir);

    foreach ($names as $name) {
        if (in_array($name, ['.', '..'])) {
            continue;
        }

        $path = $dir . DIRECTORY_SEPARATOR . $name;

        if (is_dir($path)) {
            rrmdir($path);
        } else {
            unlink($path);
        }
    }

    rmdir($dir);
}

function download(string $url, string $path): void
{
    file_put_contents($path, fopen($url, 'r'));
}

function extractZip(string $srcFile, string $destDir): void
{
    $zip = new ZipArchive();

    if ($zip->open($srcFile) !== true) {
        throw new \RuntimeException('Failed to open Python archive');
    }

    $zip->extractTo($destDir);
    $zip->close();
}

if (is_dir(BUILD_DIR)) {
    rrmdir(BUILD_DIR);
}

if (is_dir(DIST_DIR)) {
    rrmdir(DIST_DIR);
}

if (is_dir(TMP_DIR)) {
    rrmdir(TMP_DIR);
}

mkdir(BUILD_DIR);
mkdir(BUILD_DIR . '/bin');
mkdir(BUILD_DIR . '/config');
mkdir(BUILD_DIR . '/src');
mkdir(BUILD_DIR . '/src/plugins');
mkdir(DIST_DIR);
mkdir(TMP_DIR);

// Agent
echo 'Preparing Agent360...' . PHP_EOL;

copy(BASE_DIR . '/agent360/__init__.py', BUILD_DIR . '/src/__init__.py');
copy(BASE_DIR . '/agent360/agent360.py', BUILD_DIR . '/src/agent360.py');
copy(BASE_DIR . '/LICENSE', BUILD_DIR . '/LICENSE.txt');

$names = scandir(BASE_DIR . '/agent360/plugins');

foreach ($names as $name) {
    if (in_array($name, ['.', '..'])) {
        continue;
    }

    copy(BASE_DIR . '/agent360/plugins/' . $name, BUILD_DIR . '/src/plugins/' . $name);
}

copy(WIN_DIR . '/start.bat', BUILD_DIR . '/bin/start.bat');
download(AGENT_INI_URL, BUILD_DIR . '/config/agent360.ini');

// Python
echo 'Preparing Python...' . PHP_EOL;

download(PYTHON_X32_URL, TMP_DIR . '/python-x32.zip');
extractZip(TMP_DIR . '/python-x32.zip', BUILD_DIR . '/bin/python32');

$names = scandir(BUILD_DIR . '/bin/python32');

foreach ($names as $name) {
    if (in_array($name, ['.', '..'])) {
        continue;
    }

    $ext = strtolower(pathinfo($name, PATHINFO_EXTENSION));

    if ($ext === '_pth') {
        unlink(BUILD_DIR . '/bin/python32/' . $name);
    }
}

download(PYTHON_X64_URL, TMP_DIR . '/python-x64.zip');
extractZip(TMP_DIR . '/python-x64.zip', BUILD_DIR . '/bin/python64');

$names = scandir(BUILD_DIR . '/bin/python64');

foreach ($names as $name) {
    if (in_array($name, ['.', '..'])) {
        continue;
    }

    $ext = strtolower(pathinfo($name, PATHINFO_EXTENSION));

    if ($ext === '_pth') {
        unlink(BUILD_DIR . '/bin/python64/' . $name);
    }
}

download(GET_PIP_URL, TMP_DIR . '/get-pip.py');
copy(TMP_DIR . '/get-pip.py', BUILD_DIR . '/bin/python32/get-pip.py');
copy(TMP_DIR . '/get-pip.py', BUILD_DIR . '/bin/python64/get-pip.py');

// NSSM
echo 'Preparing NSSM...' . PHP_EOL;

download(NSSM_URL, TMP_DIR . '/nssm.zip');
extractZip(TMP_DIR . '/nssm.zip', BUILD_DIR);

$names = scandir(BUILD_DIR);
$nssmBase = null;

foreach ($names as $name) {
    if (str_starts_with($name, 'nssm-')) {
        $nssmBase = $name;
    }
}

if ($nssmBase === null) {
    throw new \RuntimeException('Failed to find NSSM base');
}

rename(BUILD_DIR . '/' . $nssmBase, BUILD_DIR . '/bin/nssm');
rrmdir(BUILD_DIR . '/bin/nssm/src');

// Compile
echo 'Compiling...' . PHP_EOL;

$installScriptFile = __DIR__ . '/setup.iss';

echo `"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "{$installScriptFile}"`;
