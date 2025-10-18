# SpeakTeX - Frontend

SpeakTeX 是一个将语音转换为 LaTeX 代码的 Web 应用程序。

## 功能

- 语音输入：直接说出数学公式
- LaTeX 转换：自动生成 LaTeX 代码
- 实时预览：即时查看渲染结果
- 历史记录：保存之前的转换结果

## 技术栈

- React
- Vite
- React Router
- MathJax (用于 LaTeX 渲染)

## 开发

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

### 构建生产版本

```bash
npm run build
```

### 部署到 GitHub Pages

```bash
npm run deploy
```

## 项目结构

```
/src
  /components      - React组件
  /hooks           - 自定义React钩子
  /services        - API调用服务
  /utils           - 辅助函数
```

## 部署

该项目配置为使用 GitHub Actions 自动部署到 GitHub Pages。
每次推送到 main 分支时，GitHub Actions 会自动构建并部署应用。

也可以手动部署：

```bash
npm run deploy
```

## 许可证

MIT
