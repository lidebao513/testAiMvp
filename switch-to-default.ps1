# 切换到默认的chenw@susie GitHub账号
Write-Host "切换到默认的chenw@susie GitHub账号..."
git config user.name "chenw@susie"
git config user.email "chenw@susie@example.com"
git remote set-url origin https://github.com/lidebao513/testAiMvp.git
Write-Host "已切换到默认的chenw@susie账号，远程仓库保持为 https://github.com/lidebao513/testAiMvp.git"
git config --list --local