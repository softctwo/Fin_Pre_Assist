#!/bin/bash

# ========================================
# 金融售前方案辅助系统 - 生产环境部署脚本
# ========================================

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查依赖..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    print_info "✓ 依赖检查通过"
}

# 检查环境变量文件
check_env_files() {
    print_info "检查环境变量文件..."
    
    if [ ! -f ".env.prod" ]; then
        print_error ".env.prod文件不存在"
        print_info "请复制.env.prod.example为.env.prod并配置"
        print_info "命令: cp .env.prod.example .env.prod"
        exit 1
    fi
    
    if [ ! -f "backend/.env.prod" ]; then
        print_error "backend/.env.prod文件不存在"
        print_info "请复制backend/.env.example为backend/.env.prod并配置"
        print_info "命令: cp backend/.env.example backend/.env.prod"
        exit 1
    fi
    
    # 检查是否修改了默认密码
    if grep -q "CHANGE_THIS_TO_STRONG_PASSWORD" .env.prod; then
        print_error ".env.prod中仍包含默认密码，请修改为强随机密码"
        exit 1
    fi
    
    print_info "✓ 环境变量文件检查通过"
}

# 备份数据库
backup_database() {
    print_info "备份数据库..."
    
    if docker ps | grep -q fin_pre_assist_db_prod; then
        BACKUP_DIR="./backups"
        BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
        
        mkdir -p "$BACKUP_DIR"
        
        docker exec fin_pre_assist_db_prod pg_dump -U finpre fin_pre_assist > "$BACKUP_FILE"
        
        if [ -f "$BACKUP_FILE" ]; then
            print_info "✓ 数据库已备份到: $BACKUP_FILE"
        else
            print_warning "数据库备份失败，但继续部署"
        fi
    else
        print_warning "数据库容器未运行，跳过备份"
    fi
}

# 构建镜像
build_images() {
    print_info "构建Docker镜像..."
    
    docker-compose -f docker-compose.prod.yml build --no-cache
    
    print_info "✓ 镜像构建完成"
}

# 停止旧容器
stop_containers() {
    print_info "停止旧容器..."
    
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        docker-compose -f docker-compose.prod.yml down
        print_info "✓ 旧容器已停止"
    else
        print_info "没有运行中的容器"
    fi
}

# 启动容器
start_containers() {
    print_info "启动容器..."
    
    docker-compose -f docker-compose.prod.yml up -d
    
    print_info "✓ 容器已启动"
}

# 等待服务就绪
wait_for_services() {
    print_info "等待服务就绪..."
    
    # 等待数据库就绪
    print_info "等待数据库..."
    for i in {1..30}; do
        if docker exec fin_pre_assist_db_prod pg_isready -U finpre &> /dev/null; then
            print_info "✓ 数据库就绪"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "数据库启动超时"
            exit 1
        fi
        sleep 1
    done
    
    # 等待后端就绪
    print_info "等待后端API..."
    for i in {1..60}; do
        if curl -f http://localhost:8000/health &> /dev/null; then
            print_info "✓ 后端API就绪"
            break
        fi
        if [ $i -eq 60 ]; then
            print_error "后端API启动超时"
            exit 1
        fi
        sleep 2
    done
    
    print_info "✓ 所有服务就绪"
}

# 执行数据库迁移
run_migrations() {
    print_info "执行数据库迁移..."
    
    docker exec fin_pre_assist_backend_prod python migrate.py upgrade
    
    print_info "✓ 数据库迁移完成"
}

# 健康检查
health_check() {
    print_info "执行健康检查..."
    
    # 检查所有容器状态
    CONTAINERS=(
        "fin_pre_assist_db_prod"
        "fin_pre_assist_redis_prod"
        "fin_pre_assist_backend_prod"
        "fin_pre_assist_frontend_prod"
        "fin_pre_assist_nginx_prod"
    )
    
    ALL_HEALTHY=true
    for container in "${CONTAINERS[@]}"; do
        STATUS=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2>/dev/null || echo "none")
        
        if [ "$STATUS" == "healthy" ] || [ "$STATUS" == "none" ]; then
            print_info "✓ $container: $STATUS"
        else
            print_error "✗ $container: $STATUS"
            ALL_HEALTHY=false
        fi
    done
    
    if [ "$ALL_HEALTHY" = true ]; then
        print_info "✓ 所有服务健康"
    else
        print_error "部分服务不健康，请检查日志"
        exit 1
    fi
}

# 显示部署信息
show_info() {
    echo ""
    echo "========================================="
    echo "  部署完成！"
    echo "========================================="
    echo ""
    echo "服务访问地址："
    echo "  前端应用: http://localhost:80"
    echo "  后端API:  http://localhost:80/api/v1"
    echo "  API文档:  http://localhost:80/api/v1/docs"
    echo ""
    echo "查看日志："
    echo "  docker-compose -f docker-compose.prod.yml logs -f"
    echo ""
    echo "停止服务："
    echo "  docker-compose -f docker-compose.prod.yml down"
    echo ""
    echo "重启服务："
    echo "  docker-compose -f docker-compose.prod.yml restart"
    echo ""
    echo "========================================="
}

# 主流程
main() {
    print_info "开始部署金融售前方案辅助系统（生产环境）"
    echo ""
    
    check_dependencies
    check_env_files
    
    # 询问是否备份
    read -p "是否备份数据库？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        backup_database
    fi
    
    # 询问是否继续
    read -p "开始部署？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_warning "部署已取消"
        exit 0
    fi
    
    build_images
    stop_containers
    start_containers
    wait_for_services
    run_migrations
    health_check
    show_info
    
    print_info "部署成功！🎉"
}

# 执行主流程
main "$@"
