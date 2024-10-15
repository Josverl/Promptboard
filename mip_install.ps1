
$packages = get-content .\requirements_mip.txt | foreach-object { $_.split()[0] }

if ($packages.len -gt 0) {
    # reset just to make sure
    mpremote reset 
}

foreach ($package in $packages) {
    # if line does not start with #, install the package
    if ($package -notlike "#*" -and $package -ne "") {
         mpremote mip install $package 
    }  
}

if ($packages.len -gt 0) {
    # reset just to make sure
    mpremote reset 
}



