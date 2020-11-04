/**
 * 将表格中的数据导入到excel中，以读取excel文件,需要浏览器支持es6语法,并且ie11以上
 * (1)exceljs,项目github: https://github.com/exceljs/exceljs
 * (2)fielSaver.js, 项目github: https://github.com/eligrey/FileSaver.js
 */


const excelJs = require('exceljs')  // 导入exceljs
import { saveAs } from 'file-saver'

// 将数据导入到excel
const exportDataToExcel = async (data, fileName, workSheetName="sheet1", headers=[])=>{
    const workBook1 = new excelJs.Workbook()  // 创建工作簿
    const workSheet = workBook.addWorksheet(workSheetName)  // 添加工作表
    if(headers.length === 0){
        // 如果表头为空,则使用data数组的第一个字典的键作为表头
        for(const key in data[0]){
            headers.push(key)
        }
    }
    workSheet.addRow(headers)  // 添加excel的表头
    data.forEach(item => {
        let row = []
        for(const key in item){
            row.push(item[key])
        }
        workSheet.addRow(row)  // 将数据写入工作表
    })
    const buf = await workBook.xlsx.writeBuffer()  // 将数据写入字节流
    saveAs(new Blob([buf]), fileName + '.xlsx')  // 将数据写入excel
}

export {
    exportDataToExcel
}