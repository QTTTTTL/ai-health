<template>
    <div>
        <PageHead title="知识文章">
            <template #buttons>
                <el-button type="primary">新增</el-button>
            
            </template>
        </PageHead>
        <TableSearch :formItem="formItem" @search="handleSearch"/>
    </div>
</template>
<script setup>
import PageHead from '@/components/PageHead.vue'
import TableSearch from '@/components/TableSearch.vue';

const handleSearch = async (formData) => {
    console.log(formData,'查询参数')

}
const formItem = [
    { comp: 'input', prop: 'title', label: '文章标题', placeholder: '请输入文章标题' },
    { comp: 'select', prop: 'categoryId', label: '分类',placeholder: '请选择分类' },
    { comp: 'select', prop: 'status', label: '状态', placeholder: '请输入文章内容', options: [{
       label: '草稿',
       value: '0'
    },{
       label: '已发布',
       value: '1'
    },{
       label: '已下线',
       value: '2'
    }] }
]

</script>
