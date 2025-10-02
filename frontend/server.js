const { createServer } = require('https');
const { parse } = require('url');
const next = require('next');
const fs = require('fs');
const path = require('path');

const dev = process.env.NODE_ENV !== 'production';
const hostname = 'localhost';
const port = parseInt(process.env.PORT, 10) || 3000;

const app = next({ dev, hostname, port });
const handle = app.getRequestHandler();

// HTTPS 证书路径
const certPath = path.join(__dirname, '.cert');
const keyPath = path.join(certPath, 'localhost-key.pem');
const certFilePath = path.join(certPath, 'localhost-cert.pem');

// 检查证书是否存在
const httpsEnabled = fs.existsSync(keyPath) && fs.existsSync(certFilePath);

if (httpsEnabled) {
  console.log('🔒 HTTPS 证书已找到，启用 HTTPS 模式');
} else {
  console.log('⚠️  未找到 HTTPS 证书，使用 HTTP 模式');
  console.log('💡 运行以下命令生成证书:');
  console.log('   mkdir -p .cert');
  console.log('   mkcert -key-file .cert/localhost-key.pem -cert-file .cert/localhost-cert.pem localhost 127.0.0.1');
}

app.prepare().then(() => {
  if (httpsEnabled) {
    // HTTPS 服务器
    const httpsOptions = {
      key: fs.readFileSync(keyPath),
      cert: fs.readFileSync(certFilePath),
    };

    createServer(httpsOptions, async (req, res) => {
      try {
        const parsedUrl = parse(req.url, true);
        await handle(req, res, parsedUrl);
      } catch (err) {
        console.error('Error occurred handling', req.url, err);
        res.statusCode = 500;
        res.end('internal server error');
      }
    })
      .once('error', (err) => {
        console.error(err);
        process.exit(1);
      })
      .listen(port, () => {
        console.log(`> ✅ Ready on https://${hostname}:${port}`);
        console.log(`> 环境: ${dev ? 'development' : 'production'}`);
      });
  } else {
    // HTTP 服务器（回退）
    const { createServer: createHttpServer } = require('http');

    createHttpServer(async (req, res) => {
      try {
        const parsedUrl = parse(req.url, true);
        await handle(req, res, parsedUrl);
      } catch (err) {
        console.error('Error occurred handling', req.url, err);
        res.statusCode = 500;
        res.end('internal server error');
      }
    })
      .once('error', (err) => {
        console.error(err);
        process.exit(1);
      })
      .listen(port, () => {
        console.log(`> ⚠️  Ready on http://${hostname}:${port}`);
        console.log(`> 环境: ${dev ? 'development' : 'production'}`);
      });
  }
});
