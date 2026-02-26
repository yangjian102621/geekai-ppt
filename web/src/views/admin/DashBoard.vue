<template>
  <div class="dashboard">
    <!-- 统计数据卡片区域（Mock 数据） -->
    <div class="stats-cards">
      <div class="stats-card users">
        <div class="card-icon">
          <el-icon><User /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">用户总数</div>
          <div class="card-value">
            {{ formatNumber(statsData.totalUsers) }}
          </div>
        </div>
      </div>

      <div class="stats-card presentations">
        <div class="card-icon">
          <el-icon><Document /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">PPT 总数</div>
          <div class="card-value">
            {{ formatNumber(statsData.totalPresentations) }}
          </div>
        </div>
      </div>

      <div class="stats-card today">
        <div class="card-icon">
          <el-icon><View /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">今日生成</div>
          <div class="card-value">{{ formatNumber(statsData.todayGenerated) }}</div>
        </div>
      </div>

      <div class="stats-card redemption">
        <div class="card-icon">
          <el-icon><Collection /></el-icon>
        </div>
        <div class="card-content">
          <div class="card-title">兑换码已用</div>
          <div class="card-value">
            {{ formatNumber(statsData.redemptionUsed) }}
          </div>
        </div>
      </div>
    </div>

    <!-- 图表区域（Mock 数据） -->
    <div class="charts-container">
      <div class="charts-row">
        <div class="chart-container">
          <div class="chart-title">最近 7 天 PPT 生成趋势</div>
          <div ref="trendChartRef" class="chart"></div>
        </div>

        <div class="chart-container">
          <div class="chart-title">TOP 10 主题生成数量</div>
          <div ref="barChartRef" class="chart"></div>
        </div>
      </div>

      <div class="charts-row">
        <div class="chart-container full-width">
          <div class="chart-title">PPT 状态分布</div>
          <div ref="pieChartRef" class="chart pie-chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
  import {
    Collection,
    Document,
    User,
    View,
  } from '@element-plus/icons-vue'
  import * as echarts from 'echarts'
  import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

  // 图表引用
  const trendChartRef = ref(null)
  const barChartRef = ref(null)
  const pieChartRef = ref(null)

  // 图表实例
  let trendChart = null
  let barChart = null
  let pieChart = null

  // Mock 数据：PPT 平台统计
  const statsData = ref({
    totalUsers: 1286,
    totalPresentations: 3520,
    todayGenerated: 89,
    redemptionUsed: 456,
  })

  // 最近 7 天 PPT 生成趋势（Mock）
  const trendData = ref({
    dates: ['02-04', '02-05', '02-06', '02-07', '02-08', '02-09', '02-10'],
    counts: [42, 58, 65, 78, 89, 72, 89],
  })

  // TOP 10 主题生成数量（Mock）
  const topTopics = ref([
    { title: '产品介绍', count: 520 },
    { title: '技术分享', count: 480 },
    { title: '年终总结', count: 420 },
    { title: '项目汇报', count: 380 },
    { title: '培训课件', count: 350 },
    { title: '商业计划', count: 310 },
    { title: '市场分析', count: 280 },
    { title: '周报月报', count: 250 },
    { title: '活动策划', count: 220 },
    { title: '其他', count: 300 },
  ])

  // PPT 状态分布（Mock）
  const statusDistribution = ref([
    { name: '已完成', value: 2680 },
    { name: '生成中', value: 120 },
    { name: '规划中', value: 85 },
    { name: '失败', value: 35 },
    { name: '待处理', value: 600 },
  ])

  // 数字格式化函数
  const formatNumber = (num) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M'
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K'
    }
    return num.toString()
  }

  // 初始化折线图
  const initTrendChart = () => {
    if (!trendChartRef.value) return

    trendChart = echarts.init(trendChartRef.value)

    const option = {
      tooltip: {
        trigger: 'axis',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#333',
        textStyle: {
          color: '#fff',
        },
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: trendData.value.dates,
        axisLine: {
          lineStyle: {
            color: '#e0e0e0',
          },
        },
        axisTick: {
          show: false,
        },
      },
      yAxis: {
        type: 'value',
        axisLine: {
          show: false,
        },
        axisTick: {
          show: false,
        },
        splitLine: {
          lineStyle: {
            color: '#f0f0f0',
          },
        },
      },
      series: [
        {
          name: '生成数量',
          type: 'line',
          smooth: true,
          symbol: 'circle',
          symbolSize: 6,
          lineStyle: {
            width: 3,
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 1,
              y2: 0,
              colorStops: [
                {
                  offset: 0,
                  color: '#409EFF',
                },
                {
                  offset: 1,
                  color: '#67C23A',
                },
              ],
            },
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                {
                  offset: 0,
                  color: 'rgba(64, 158, 255, 0.3)',
                },
                {
                  offset: 1,
                  color: 'rgba(103, 194, 58, 0.1)',
                },
              ],
            },
          },
          data: trendData.value.counts,
        },
      ],
    }

    trendChart.setOption(option)
  }

  // 初始化柱状图
  const initBarChart = () => {
    if (!barChartRef.value) return

    barChart = echarts.init(barChartRef.value)

    const option = {
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
        },
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#333',
        textStyle: {
          color: '#fff',
        },
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: '10%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: topTopics.value.map((item) => item.title),
        axisLabel: {
          interval: 0,
          rotate: 45,
          fontSize: 10,
        },
        axisLine: {
          lineStyle: {
            color: '#e0e0e0',
          },
        },
      },
      yAxis: {
        type: 'value',
        axisLine: {
          show: false,
        },
        splitLine: {
          lineStyle: {
            color: '#f0f0f0',
          },
        },
      },
      series: [
        {
          name: '生成数',
          type: 'bar',
          data: topTopics.value.map((item) => item.count),
          itemStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                {
                  offset: 0,
                  color: '#409EFF',
                },
                {
                  offset: 1,
                  color: '#67C23A',
                },
              ],
            },
            borderRadius: [4, 4, 0, 0],
          },
          label: {
            show: true,
            position: 'top',
            formatter: '{c}',
            fontSize: 10,
          },
        },
      ],
    }

    barChart.setOption(option)
  }

  // 初始化饼图
  const initPieChart = () => {
    if (!pieChartRef.value) return

    pieChart = echarts.init(pieChartRef.value)

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)',
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        borderColor: '#333',
        textStyle: {
          color: '#fff',
        },
      },
      legend: {
        orient: 'vertical',
        left: 'left',
        top: 'center',
        textStyle: {
          fontSize: 12,
        },
      },
      series: [
        {
          name: 'PPT 数量',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['60%', '50%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 8,
            borderColor: '#fff',
            borderWidth: 2,
          },
          label: {
            show: false,
            position: 'center',
          },
          emphasis: {
            label: {
              show: true,
              fontSize: '16',
              fontWeight: 'bold',
            },
          },
          labelLine: {
            show: false,
          },
          data: statusDistribution.value,
        },
      ],
    }

    pieChart.setOption(option)
  }

  // 窗口大小变化处理
  const handleResize = () => {
    if (trendChart) trendChart.resize()
    if (barChart) barChart.resize()
    if (pieChart) pieChart.resize()
  }

  // 组件挂载
  onMounted(() => {
    nextTick(() => {
      initTrendChart()
      initBarChart()
      initPieChart()

      // 监听窗口大小变化
      window.addEventListener('resize', handleResize)
    })
  })

  // 组件卸载
  onBeforeUnmount(() => {
    if (trendChart) {
      trendChart.dispose()
      trendChart = null
    }
    if (barChart) {
      barChart.dispose()
      barChart = null
    }
    if (pieChart) {
      pieChart.dispose()
      pieChart = null
    }

    window.removeEventListener('resize', handleResize)
  })
</script>

<style scoped lang="scss">
  .dashboard {
    background: #f8f9fa;

    // 统计数据卡片
    .stats-cards {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
      gap: 20px;
      margin-bottom: 30px;

      .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 24px;
        color: white;
        display: flex;
        align-items: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;

        &:hover {
          transform: translateY(-5px);
          box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        }

        &.users {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        &.presentations {
          background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        }

        &.today {
          background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        &.redemption {
          background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        }

        .card-icon {
          font-size: 32px;
          margin-right: 16px;
          opacity: 0.9;
        }

        .card-content {
          .card-title {
            font-size: 14px;
            opacity: 0.9;
            margin-bottom: 4px;
          }

          .card-value {
            font-size: 28px;
            font-weight: bold;
            line-height: 1;
          }
        }
      }
    }

    // 图表容器
    .charts-container {
      .charts-row {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-bottom: 20px;

        .chart-container {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);

          &.full-width {
            grid-column: 1 / -1;
          }

          .chart-title {
            font-size: 16px;
            font-weight: 600;
            color: #303133;
            margin-bottom: 16px;
            text-align: center;
          }

          .chart {
            height: 300px;
            width: 100%;

            &.pie-chart {
              height: 400px;
            }
          }
        }
      }
    }
  }

  // 响应式设计
  @media (max-width: 1200px) {
    .dashboard {
      .charts-container {
        .charts-row {
          grid-template-columns: 1fr;

          .chart-container {
            &.full-width {
              grid-column: 1;
            }
          }
        }
      }
    }
  }

  @media (max-width: 768px) {
    .dashboard {
      .stats-cards {
        grid-template-columns: 1fr;
        gap: 15px;
      }

      .charts-container {
        .charts-row {
          gap: 15px;

          .chart-container {
            padding: 15px;

            .chart {
              height: 250px;

              &.pie-chart {
                height: 300px;
              }
            }
          }
        }
      }
    }
  }
</style>
