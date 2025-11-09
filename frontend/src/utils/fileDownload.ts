/**
 * 文件下载工具函数
 */

/**
 * 处理文件下载
 * @param response - axios响应对象
 * @param filename - 建议的文件名
 */
export const handleFileDownload = (response: any, filename?: string) => {
  // 检查响应是否包含文件内容
  const contentType = response.headers?.['content-type'] || '';
  const isFileDownload = contentType.includes('application/') ||
                        contentType.includes('application/octet-stream') ||
                        response.headers?.['content-disposition']?.includes('attachment');

  if (isFileDownload) {
    // 获取文件内容
    const blob = new Blob([response.data], { type: contentType });

    // 获取文件名
    const contentDisposition = response.headers?.['content-disposition'];
    let finalFilename = filename;

    if (contentDisposition) {
      // 从Content-Disposition头中提取文件名
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      if (filenameMatch?.[1]) {
        finalFilename = filenameMatch[1].replace(/['"]/g, '');
      }
    }

    // 创建下载链接
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = finalFilename || 'download';

    // 触发下载
    document.body.appendChild(link);
    link.click();

    // 清理
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);

    return true;
  }

  return false;
};