/*
* 解析出迅雷,快车,旋风,f2syou下载地址的URL
* */


import bs64 from './bs64'


const reg = /(^thunder:|^flashget:|^qqdl:|^fs2you:)\/\//i  // 判断url是否有效的正则
const re1 = /^thunder:\/\//i  // 匹配迅雷下载的正则
const re2 = /^flashget:\/\//i  // 匹配快车下载的正则
const re3 = /^qqdl:\/\//i  // 匹配旋风下载的正则
const re4 = /^fs2you:\/\//i  // 匹配f2syou下载的正则
const rea = /^AA|ZZ$/gi
const reb = /^\[FLASHGET\]|\[FLASHGET\]$/gi
const rec = /\s+$/g
const red = /\s+$/g


// 去除url中的空白符以及\v
const regString = (s) => {
  return s.replace(/\s|　|\n|\r|\t|\v/g, '')
}


const checkUrl = (url) => {
  const reg1 = /^(https?|ftp|thunder|flashget|qqdl|fs2you):\/\//gi;
  return reg1.test(url)
}


const doits = (url, reX, reTmp, sid) => {
  let v = url.replace(reX,'')  // 去除前缀
  v = bs64.decode64(v).replace(reTmp, '') // 先将url使用bs64解码,然后将对应的AA或者ZZ替换成''
  if (v === '') {
    return false  // 原始的url有错误
  }
  if (!(/^(https?|ftp):\/\//i.test(v))) {
    v = 'http://' + v;
  }
  return v  // 返回解析后的url
}


// 将输入的url解析成可供aria2下载的url

const parseDownLoadUrl = (url) => {
  let result = null
  let ys = regString(url)  // 去除空白符以及\v
  if (ys === '') {
    result = false
  }
  else {
    if (reg.test(ys)) {
      // 原始的url不是这四种格式
      ys = ys.replace(/\/+$/, '')  // 去除url中的/
      if (re1.test(ys)) {
        result = doits(url, re1, rea, 'xl')
      }
      if (re2.test(ys)) {
        result = doits(url, re2, reb, 'kc')
      }
      if (re3.test(ys)) {
        result = doits(url, re3, rec, 'xf')
      }
      if (re4.test(ys)) {
        result = doits(url, re4, red, 'fs')
      }
    } else {
      if (!checkUrl(ys)) {
        result = false  // 原始的url格式既不是这四种也不是http(s),ftp开头
      } else {
        result = ys  // 原始的格式就是http(s),ftp
      }
    }
  }
  return result
}


export {
  parseDownLoadUrl,
  checkUrl
}
