<template>
  <div id="app">
    <div class="layout">
      <aside class="sidebar">
        <div class="logo">
          <span class="logo-icon">👰</span>
          <span class="logo-text">伴娘团协同</span>
        </div>
        <nav class="nav-menu">
          <router-link to="/orders" class="nav-item">
            <span class="nav-icon">📋</span>
            <span>订单列表</span>
          </router-link>
          <router-link to="/tasks" class="nav-item">
            <span class="nav-icon">📝</span>
            <span>任务看板</span>
          </router-link>
          <router-link to="/checklist" class="nav-item">
            <span class="nav-icon">✅</span>
            <span>准备清单</span>
          </router-link>
          <router-link to="/timeline" class="nav-item">
            <span class="nav-icon">📅</span>
            <span>当天流程</span>
          </router-link>
          <router-link to="/checkin" class="nav-item">
            <span class="nav-icon">✅</span>
            <span>现场签到</span>
          </router-link>
          <router-link to="/guests" class="nav-item">
            <span class="nav-icon">👥</span>
            <span>宾客管理</span>
          </router-link>
          <router-link to="/production" class="nav-item">
            <span class="nav-icon">📆</span>
            <span>生产排期</span>
          </router-link>
          <router-link to="/emergency" class="nav-item">
            <span class="nav-icon">🆘</span>
            <span>应急联系人</span>
          </router-link>
          <router-link to="/stats" class="nav-item">
            <span class="nav-icon">📊</span>
            <span>数据统计</span>
          </router-link>
          <router-link to="/budget" class="nav-item">
            <span class="nav-icon">💰</span>
            <span>预算报销</span>
          </router-link>
          <router-link to="/material" class="nav-item">
            <span class="nav-icon">📦</span>
            <span>物资追踪</span>
          </router-link>
        </nav>
        <div class="sidebar-footer">
          <div class="wedding-info">
            <div class="wedding-title">{{ weddingInfo.bride_name }} & {{ weddingInfo.groom_name }}</div>
            <div class="wedding-date">💒 {{ weddingInfo.wedding_date }}</div>
          </div>
        </div>
      </aside>
      <main class="main-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getWedding } from '@/api/wedding'

const weddingInfo = ref({
  bride_name: '新娘',
  groom_name: '新郎',
  wedding_date: '2025-10-01',
  venue: ''
})

onMounted(async () => {
  try {
    const res = await getWedding(1)
    if (res) {
      weddingInfo.value = res
    }
  } catch (e) {
    console.log('加载婚礼信息失败')
  }
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.layout {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

.sidebar {
  width: 240px;
  background: linear-gradient(180deg, #ff6b9d 0%, #c44569 100%);
  color: white;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.logo {
  padding: 24px 20px;
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 1px solid rgba(255,255,255,0.2);
}

.logo-icon {
  font-size: 32px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
}

.nav-menu {
  flex: 1;
  padding: 16px 12px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  color: rgba(255,255,255,0.9);
  text-decoration: none;
  border-radius: 8px;
  margin-bottom: 4px;
  transition: all 0.3s;
  font-size: 14px;
}

.nav-item:hover {
  background: rgba(255,255,255,0.15);
  color: white;
}

.nav-item.router-link-active {
  background: rgba(255,255,255,0.2);
  color: white;
  font-weight: 500;
}

.nav-icon {
  font-size: 18px;
  width: 24px;
  text-align: center;
}

.sidebar-footer {
  padding: 20px;
  border-top: 1px solid rgba(255,255,255,0.2);
}

.wedding-info {
  background: rgba(255,255,255,0.15);
  border-radius: 8px;
  padding: 12px;
}

.wedding-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
}

.wedding-date {
  font-size: 12px;
  opacity: 0.9;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}
</style>
