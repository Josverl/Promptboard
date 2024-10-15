
# TODO 
# mpflash custom firmware 

# mip install 
# .\mip_install.ps1

# TODO : backup or avoid overwiting the config file
# Create a string with the current date-time
$dateTimeString = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$backupFileName = "config_$dateTimeString.py"
Copy-Item -Path "e:\config.py" -Destination "e:\$backupFileName" -Force -Verbose

# copy Source to Target
copy -Force -Verbose -Path .\src\* -Destination e:\

# final reset
mpremote reset