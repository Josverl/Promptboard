
$packages = get-content .\requirements_mip.txt | foreach-object { $_.split()[0] }

foreach ($package in $packages) {
    # if line does not start with #, install the package
    if ($package -notlike "#*" -and $package -ne "") {
         mpremote mip install $package 
    }  
}




