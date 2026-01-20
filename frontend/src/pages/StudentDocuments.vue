<template>
  <div class="documents-container">
    <el-container>
      <el-header class="header">
        <div class="header-left">
          <h1>学生文档评阅</h1>
        </div>
        <div class="header-right">
          <el-tooltip content="消息箱" placement="bottom">
            <el-badge :value="unreadCount > 0 ? unreadCount : ''" class="header-icon" @click="goToInbox">
              <el-icon class="icon-button"><Notification /></el-icon>
            </el-badge>
          </el-tooltip>
          <el-dropdown>
            <el-icon class="user-icon"><User /></el-icon>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>{{ authStore.user?.username }}</el-dropdown-item>
                <el-dropdown-item divided @click="goToProfile">个人信息</el-dropdown-item>
                <el-dropdown-item @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-container>
        <el-aside width="200px" class="aside">
          <el-menu router :default-active="activeMenu">
            <el-menu-item index="/dashboard" route="/dashboard">
              <template #title>首页</template>
            </el-menu-item>
            <el-menu-item v-if="isStudent" index="/review-teacher" route="/review-teacher">
              <template #title>教师评价</template>
            </el-menu-item>
            <el-menu-item index="/teacher-management" route="/teacher-management">
              <template #title>学生管理</template>
            </el-menu-item>
            <el-menu-item index="/student-documents" route="/student-documents">
              <template #title>毕设评阅</template>
            </el-menu-item>
            <el-menu-item index="/review-statistics" route="/review-statistics">
              <template #title>评价统计</template>
            </el-menu-item>
            <el-menu-item index="/teacher-ratings-display" route="/teacher-ratings-display">
              <template #title>评价浏览</template>
            </el-menu-item>
            <el-menu-item index="/questions" route="/questions">
              <template #title>问题中心</template>
            </el-menu-item>
          </el-menu>
        </el-aside>

        <el-main>
          <!-- 文档管理卡片 -->
          <el-card class="documents-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <span>学生毕业设计文档</span>
                <div class="filters">
                  <el-select v-model="filterDocType" placeholder="文档类型" clearable @change="loadDocuments" style="width: 120px; margin-right: 10px">
                    <el-option label="选题报告" value="proposal" />
                    <el-option label="大纲" value="outline" />
                    <el-option label="初稿" value="draft" />
                    <el-option label="终稿" value="final" />
                  </el-select>
                  <el-select v-model="filterStage" placeholder="上交阶段" clearable @change="loadDocuments" style="width: 120px">
                    <el-option label="早期" value="early" />
                    <el-option label="中期" value="mid" />
                    <el-option label="最终" value="final" />
                  </el-select>
                </div>
              </div>
            </template>

            <!-- 文档列表 - 按学生分组 -->
            <el-tree
              :data="groupedDocuments"
              node-key="id"
              :props="treeProps"
              default-expand-all
              style="width: 100%"
              :loading="loading"
            >
              <template #default="{ node, data }">
                <!-- 学生节点 -->
                <div v-if="data.isStudent" style="display: flex; align-items: center; width: 100%; flex: 1">
                  <strong style="color: #333; margin-right: 20px">{{ data.label }}</strong>
                  <el-tag v-if="data.totalDocs" style="margin-left: auto">
                    共 {{ data.totalDocs }} 个文档
                  </el-tag>
                </div>
                
                <!-- 文档节点 -->
                <div v-else style="display: flex; align-items: center; width: 100%; flex: 1; font-size: 14px">
                  <span style="margin-right: 15px; min-width: 150px">📄 {{ data.label }}</span>
                  <el-tag :type="getDocTypeTag(data.document_type)" style="margin-right: 10px">
                    {{ getDocTypeName(data.document_type) }}
                  </el-tag>
                  <el-tag style="margin-right: 10px">{{ getStageName(data.submission_stage) }}</el-tag>
                  <span style="margin-right: 15px; color: #909399; min-width: 160px">
                    {{ formatTime(null, data.submitted_at) }}
                  </span>
                  <el-badge :value="data.reminder_count" class="badge-count" style="margin-right: 15px" />
                  <el-tag :type="data.teacher_feedback ? 'success' : 'info'" style="margin-right: 15px">
                    {{ data.teacher_feedback ? '已反馈' : '未反馈' }}
                  </el-tag>
                  <div style="margin-left: auto; display: flex; gap: 8px">
                    <el-button link type="primary" size="small" @click.stop="handleDownload(data)">
                      下载
                    </el-button>
                    <el-button link type="primary" size="small" @click.stop="handleViewFeedback(data)">
                      查看评价
                    </el-button>
                    <el-button link type="success" size="small" @click.stop="handleAddFeedback(data)">
                      评价
                    </el-button>
                    <el-button link type="warning" size="small" @click.stop="handleRemindSubmission(data)">
                      催交
                    </el-button>
                  </div>
                </div>
              </template>
            </el-tree>

            <!-- 分页 -->
            <div style="margin-top: 20px; text-align: right">
              <el-pagination
                v-model:current-page="currentPage"
                v-model:page-size="pageSize"
                :page-sizes="[10, 20, 50]"
                :total="total"
                layout="total, sizes, prev, pager, next, jumper"
                @change="loadDocuments"
              />
            </div>
          </el-card>
        </el-main>
      </el-container>
    </el-container>

    <!-- 评价对话框 -->
    <el-dialog v-model="showFeedbackDialog" title="添加评价" width="600px">
      <div v-if="selectedDocument">
        <el-form label-width="100px">
          <el-form-item label="学生">
            <span>{{ selectedDocument.student_real_name }} ({{ selectedDocument.student_username }})</span>
          </el-form-item>
          <el-form-item label="文件">
            <span>{{ selectedDocument.filename }}</span>
          </el-form-item>
          <el-form-item label="评价内容" required>
            <el-input
              v-model="feedbackContent"
              type="textarea"
              :rows="6"
              placeholder="请输入对学生的评价和建议"
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showFeedbackDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSubmitFeedback" :loading="feedbackLoading">
          提交评价
        </el-button>
      </template>
    </el-dialog>

    <!-- 查看评价对话框 -->
    <el-dialog v-model="showViewFeedbackDialog" title="查看评价" width="600px">
      <div v-if="selectedDocument">
        <el-form label-width="100px">
          <el-form-item label="学生">
            <span>{{ selectedDocument.student_real_name }} ({{ selectedDocument.student_username }})</span>
          </el-form-item>
          <el-form-item label="文件">
            <span>{{ selectedDocument.filename }}</span>
          </el-form-item>
          <el-form-item label="评价内容">
            <el-input
              v-model="selectedDocument.teacher_feedback"
              type="textarea"
              :rows="6"
              disabled
            />
          </el-form-item>
          <el-form-item v-if="selectedDocument.feedback_at" label="评价时间">
            <span>{{ formatTime(null, selectedDocument.feedback_at) }}</span>
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="showViewFeedbackDialog = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { authAPI } from '@/api/auth'
import { teacherAPI } from '@/api/teacher'
import { messagesAPI } from '@/api/messages'
import { ArrowDown, Notification, User } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

// 状态
const loading = ref(false)
const activeMenu = ref('/student-documents')
const unreadCount = ref(0)
const documentList = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const filterDocType = ref('')
const filterStage = ref('')

// 树组件配置
const treeProps = {
  children: 'children',
  label: 'label'
}

// 分组后的文档
const groupedDocuments = computed(() => {
  const grouped = {}
  
  documentList.value.forEach(doc => {
    const key = `${doc.student_id}-${doc.student_real_name}`
    if (!grouped[key]) {
      grouped[key] = {
        id: key,
        label: `${doc.student_real_name} (${doc.student_username})`,
        isStudent: true,
        children: [],
        totalDocs: 0
      }
    }
    grouped[key].children.push({
      id: doc.id,
      label: doc.filename,
      isStudent: false,
      ...doc
    })
    grouped[key].totalDocs = grouped[key].children.length
  })
  
  return Object.values(grouped)
})

// 对话框状态
const showFeedbackDialog = ref(false)
const showViewFeedbackDialog = ref(false)
const selectedDocument = ref(null)
const feedbackContent = ref('')
const feedbackLoading = ref(false)

// 加载文档列表
const loadDocuments = async () => {
  loading.value = true
  try {
    const response = await teacherAPI.getStudentDocuments(
      currentPage.value,
      pageSize.value,
      null,
      filterDocType.value,
      filterStage.value
    )

    if (response.data.code === 200) {
      documentList.value = response.data.data.documents
      total.value = response.data.data.total
    } else {
      ElMessage.error(response.data.message || '加载失败')
    }
  } catch (error) {
    console.error('Load documents error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '加载失败')
  } finally {
    loading.value = false
  }
}

// 加载未读消息数
const loadUnreadCount = async () => {
  try {
    const response = await messagesAPI.getUnreadCount()
    if (response.data.code === 200) {
      unreadCount.value = response.data.data.unread
    }
  } catch (error) {
    console.error('Get unread count error:', error)
  }
}

// 查看评价
const handleViewFeedback = (doc) => {
  if (!doc.teacher_feedback) {
    ElMessage.info('暂无评价')
    return
  }
  selectedDocument.value = doc
  showViewFeedbackDialog.value = true
}

// 添加评价
const handleAddFeedback = (doc) => {
  selectedDocument.value = doc
  feedbackContent.value = doc.teacher_feedback || ''
  showFeedbackDialog.value = true
}

// 提交评价
const handleSubmitFeedback = async () => {
  if (!feedbackContent.value.trim()) {
    ElMessage.warning('请输入评价内容')
    return
  }

  feedbackLoading.value = true
  try {
    const response = await teacherAPI.addDocumentFeedback(
      selectedDocument.value.id,
      feedbackContent.value
    )

    if (response.data.code === 200) {
      ElMessage.success('评价已提交')
      showFeedbackDialog.value = false
      feedbackContent.value = ''
      await loadDocuments()
    } else {
      ElMessage.error(response.data.message || '提交失败')
    }
  } catch (error) {
    console.error('Submit feedback error:', error)
    ElMessage.error(error.response?.data?.message || error.message || '提交失败')
  } finally {
    feedbackLoading.value = false
  }
}

// 催交
const handleRemindSubmission = async (doc) => {
  ElMessageBox.confirm(
    `确定要催交 ${doc.student_real_name} 的《${doc.filename}》吗？`,
    '催交确认',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    }
  ).then(async () => {
    try {
      const response = await teacherAPI.remindStudentSubmission(doc.id)

      if (response.data.code === 200) {
        ElMessage.success(`已催交（第 ${response.data.data.reminder_count} 次）`)
        await loadDocuments()
      } else {
        ElMessage.error(response.data.message || '催交失败')
      }
    } catch (error) {
      console.error('Remind error:', error)
      ElMessage.error(error.response?.data?.message || error.message || '催交失败')
    }
  }).catch(() => {
    // 取消操作
  })
}

// 下载文件
const handleDownload = async (doc) => {
  try {
    const response = await teacherAPI.downloadStudentDocument(doc.id)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', doc.filename)
    document.body.appendChild(link)
    link.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(link)
  } catch (error) {
    ElMessage.error('下载失败')
  }
}

// 格式化时间
const formatTime = (row, dateStr = null) => {
  const date = dateStr ? new Date(dateStr) : (row?.created_at ? new Date(row.created_at) : null)
  if (!date) return '-'
  return date.toLocaleString('zh-CN')
}

// 获取文档类型名称
const getDocTypeName = (type) => {
  const typeMap = {
    'proposal': '选题报告',
    'outline': '大纲',
    'draft': '初稿',
    'final': '终稿'
  }
  return typeMap[type] || type
}

// 获取文档类型标签颜色
const getDocTypeTag = (type) => {
  const typeMap = {
    'proposal': 'info',
    'outline': '',
    'draft': 'warning',
    'final': 'success'
  }
  return typeMap[type] || 'info'
}

// 获取阶段名称
const getStageName = (stage) => {
  const stageMap = {
    'early': '早期',
    'mid': '中期',
    'final': '最终'
  }
  return stageMap[stage] || stage
}

// 导航
const goToInbox = () => {
  router.push('/inbox')
}

const goToProfile = () => {
  router.push('/profile')
}

const handleLogout = async () => {
  try {
    await authAPI.logout()
    authStore.clearAuth()
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
    authStore.clearAuth()
    router.push('/login')
  }
}

// 初始化
onMounted(() => {
  loadDocuments()
  loadUnreadCount()
})
</script>

<style scoped lang="scss">
.documents-container {
  height: 100vh;
  display: flex;
  flex-direction: column;

  :deep(.el-container) {
    height: 100%;
  }

  .header {
    background-color: #667eea;
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 20px;

    .header-left h1 {
      margin: 0;
      font-size: 24px;
    }

    .header-right {
      display: flex;
      align-items: center;
      gap: 20px;

      .header-icon {
        cursor: pointer;
        font-size: 20px;
        transition: all 0.3s;

        .icon-button {
          color: white;
          transition: transform 0.3s;

          &:hover {
            transform: scale(1.2);
          }
        }

        :deep(.el-badge__content) {
          background-color: #f56c6c;
        }
      }

      .user-icon {
        cursor: pointer;
        font-size: 24px;
        color: white;
        transition: transform 0.3s;

        &:hover {
          transform: scale(1.1);
        }
      }
    }
  }

  .aside {
    background-color: #f5f7fa;
    border-right: 1px solid #dcdfe6;
  }

  :deep(.el-main) {
    padding: 20px;
    overflow-y: auto;
  }

  .documents-card {
    margin: 0;
    border-radius: 6px;
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;

    .filters {
      display: flex;
      gap: 10px;
    }
  }

  .el-table {
    margin-top: 10px;
  }

  :deep(.el-pagination) {
    margin-top: 20px;
  }

  .badge-count {
    :deep(.el-badge__content) {
      background-color: #f56c6c;
    }
  }
}
</style>
