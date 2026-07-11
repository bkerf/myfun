#!/bin/zsh

log "========== 开始定义函数 =========="

# 第一个参数分割大小，第二个参数文件
mysplit(){
    split -b "${1}m" "$2" "${2}.split."
    for file in "${2}.split."*; do
        mv "$file" "${file}.log"
    done
    ll
}

# Wrap git. On errors, print an additional line in red.
git(){
    command git "$@"
    local exitCode=$?
    if [ $exitCode -ne 0 ]; then
        printf "\033[0;31mERROR: git exited with code $exitCode\033[0m\n"
    fi
    return $exitCode
}

function codep(){
    code "$1" --proxy-server="socks5://127.0.0.1:7070"
}

# 杀端口
function killport() {
    local port=$1
    log "尝试杀死端口 $port"
    local lst
    lst=$(lsof -iTCP:"$port" -t)
    if [ -n "$lst" ]; then
        log "端口 $port 被占用，PID: $lst，正在杀死..."
        kill -9 "$lst"
        log "已杀死 PID $lst，端口 $port 现已空闲"
    else
        log "端口 $port 未被占用"
    fi
}

function mgn() {
    git log --reverse --pretty=%H master | grep -A 1 "$(git rev-parse HEAD)" | tail -n1 | xargs git checkout
}

function mgp() {
    git checkout HEAD^1
}

function clear_idea() {
    rm -rf *.iml .idea out
    log "已清理 *.iml, .idea 和 out 目录"
}

# API 生成函数
function api() {
    if grep -Fxq "gem 'rails-admin-scaffold', git: 'git@www.it-place.org:oyqx17/rails-admin-scaffold.git'" Gemfile; then
        log "rails-admin-scaffold 已存在于 Gemfile 中"
    else
        log "向 Gemfile 添加 rails-admin-scaffold 并执行 bundle install"
        echo "gem 'rails-admin-scaffold', git: 'git@www.it-place.org:oyqx17/rails-admin-scaffold.git'" >> Gemfile
        bundle install
    fi
    log "生成 API Controller: Model=$1, Namespace=$2, Attributes=$3"
    eval "rails g admin:scaffold_controller \"$1\" \"$3\" --prefix_name=\"$2\" --force"
}

function apib() {
    log "生成带 Bootstrap 的 API Controller: Model=$1, Namespace=$2, Attributes=$3"
    eval "rails g admin:scaffold_controller \"$1\" \"$3\" --prefix_name=\"$2\" --bootstrap --force"
}

function logcat() {
    adb logcat | grep -F "$(adb shell ps | grep "$1" | tr -s ' ' | cut -d' ' -f2)"
}

function d2u() {
    find "$1" -type f -print0 | xargs -0 dos2unix -f
}

function myfun(){
    code "/Users/ok/github/myfun"
}

function enable(){
    xattr -cr "$1"
}

# FileSearch
function f() {
    find . -iname "*$1*" "${@:2}"
}

function up_test() {
    rsync "$1" ec2-user@dl.taashgold.com:~/webapps/apks/
    echo "https://pic.taashgold.com/apks/taashgold.apk"
}

function fd() {
    find . -iname "*$1*" "${@:2}" -delete
}

function r() {
    grep "$1" "${@:2}" -R .
}

function rag() {
    ag "$1" "${@:2}" -R .
}

# mkdir and cd
function mkcd() {
    mkdir -p "$@" && cd "$_"
}

function create_project(){
    CreateProject.py -p "$1" -o .
}

# 恢复文件夹状态
function git_checkout() {
    local folder="$1"
    log "恢复文件夹 $folder 状态"
    git checkout -- "$folder/" && git clean -f "$folder/"
}

# 从Git版本控制中移除指定文件夹，同时保留本地副本，并更新 .gitignore
function git_untrack_and_ignore() {
    local folder="$1"
    log "添加 $folder 到 .gitignore"
    echo "$folder/" >> .gitignore

    log "从版本控制中移除 $folder"
    git rm -r --cached "$folder"

    log "提交更改到仓库"
    git commit -m "Remove $folder from version control and update .gitignore"

    log "推送更改到远程仓库"
    git push
}

function gitPullAll() {
    log "拉取所有远程分支"
    git fetch origin
    for remote in $(git branch -r | grep -v master); do
        local branch="${remote#origin/}"
        if ! git show-ref --verify --quiet "refs/heads/$branch"; then
            git branch --track "$branch" "$remote"
            log "创建并跟踪分支 $branch"
        else
            log "分支 '$branch' 已存在"
        fi
    done
}

# 查找超过10M的文件
alias fb='find . -type f -size +10M -exec du -h {} +'

# 重写 make 函数
function tabby_run() {
    log "启动 Tabby 服务器，使用 Metal 硬件加速并指定模型"
    tabby serve --device metal --model StarCoder-1B --chat-model Qwen2-1.5B-Instruct
}

# objdump 查找符号并复制到剪贴板
function find_symbol {
    local so_file="$1"
    local symbol="$2"
    if [[ -z "$so_file" || -z "$symbol" ]]; then
        echo "Usage: find_symbol [SO_FILE] [SYMBOL]"
        return 1
    fi
    if [[ ! -e "$so_file" ]]; then
        echo "Error: Shared object file does not exist: $so_file"
        return 1
    fi
    local mangled_name
    mangled_name=$(objdump -tT "$so_file" | grep "$symbol" | tail -1 | awk '{print $NF}')
    echo "$mangled_name" | pbcopy
    log "已复制最后一个匹配的符号名到剪贴板: $mangled_name"
}

# 生成强密码，带位数
function genPwd() {
    head -c 256 /dev/random | openssl sha512 -binary | base64 | tr -dc A-Za-z0-9 | cut -b1-"$1"
}

# 定义 docker-tags 函数
function docker-tags () {
    local name=$1
    local url="https://registry.hub.docker.com/v2/repositories/library/$name/tags/?page_size=100"
    (
        while [[ -n "$url" ]]; do
            >&2 echo -n "."
            local content
            content=$(curl -s "$url" | python3 -c 'import sys, json; data = json.load(sys.stdin); print(data.get("next", "") or ""); print("\n".join([x["name"] for x in data["results"]]))')
            url=$(echo "$content" | head -n 1)
            echo "$content" | tail -n +2
        done
        >&2 echo
    ) | cut -d '-' -f 1 | sort --version-sort | uniq
}

# fetch branch data without checkout
function gf() {
    local branch="$1"
    git fetch origin "$branch:$branch" --update-head-ok
}

log "========== 函数定义完成 =========="
