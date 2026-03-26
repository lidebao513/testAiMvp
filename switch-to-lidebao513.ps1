# 切换到lidebao513 GitHub账号
Write-Host "切换到lidebao513 GitHub账号..."
git config user.name "lidebao513"
git config user.email "690372397@qq.com"
git remote set-url origin https://github.com/lidebao513/testAiMvp.git
Write-Host "已切换到lidebao513账号，远程仓库设置为 https://github.com/lidebao513/testAiMvp.git"
git config --list --local