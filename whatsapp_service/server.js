const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const http = require('http');

// Create WhatsApp client with persistent session
const client = new Client({
    authStrategy: new LocalAuth({
        dataPath: './.wwebjs_auth'
    }),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

let isReady = false;

// Generate QR code for authentication
client.on('qr', (qr) => {
    console.log('QR Code received. Scan this with WhatsApp:');
    qrcode.generate(qr, { small: true });
});

// Client is ready
client.on('ready', () => {
    console.log('WhatsApp Client is ready!');
    isReady = true;
});

client.on('authenticated', () => {
    console.log('WhatsApp authenticated successfully');
});

client.on('auth_failure', (msg) => {
    console.error('Authentication failed:', msg);
});

client.on('disconnected', (reason) => {
    console.log('Client was disconnected:', reason);
    isReady = false;
});

// Initialize the client
client.initialize();

// Create HTTP server to handle message requests
const server = http.createServer(async (req, res) => {
    // Set CORS headers
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    
    if (req.method === 'OPTIONS') {
        res.writeHead(200);
        res.end();
        return;
    }
    
    if (req.method === 'POST' && req.url === '/send') {
        let body = '';
        
        req.on('data', chunk => {
            body += chunk.toString();
        });
        
        req.on('end', async () => {
            try {
                const data = JSON.parse(body);
                const { phone_number, message } = data;
                
                if (!phone_number || !message) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'phone_number and message are required' }));
                    return;
                }
                
                if (!isReady) {
                    res.writeHead(503, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ error: 'WhatsApp client is not ready. Please authenticate first.' }));
                    return;
                }
                
                // Format phone number (remove any non-digits and add @c.us)
                const formattedNumber = phone_number.replace(/\D/g, '') + '@c.us';
                
                // Check if number is registered on WhatsApp
                const isRegistered = await client.isRegisteredUser(formattedNumber);
                
                if (!isRegistered) {
                    res.writeHead(400, { 'Content-Type': 'application/json' });
                    res.end(JSON.stringify({ 
                        error: `Number ${phone_number} is not registered on WhatsApp` 
                    }));
                    return;
                }
                
                // Send message
                await client.sendMessage(formattedNumber, message);
                
                res.writeHead(200, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ 
                    success: true, 
                    message: `Message sent to ${phone_number}` 
                }));
            } catch (error) {
                console.error('Error:', error);
                res.writeHead(500, { 'Content-Type': 'application/json' });
                res.end(JSON.stringify({ error: error.message }));
            }
        });
    } else if (req.method === 'GET' && req.url === '/status') {
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
            ready: isReady,
            message: isReady ? 'WhatsApp client is ready' : 'WhatsApp client is not ready. Please scan QR code.'
        }));
    } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Not found' }));
    }
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`WhatsApp service running on http://localhost:${PORT}`);
    console.log('Endpoints:');
    console.log('  POST /send - Send WhatsApp message');
    console.log('  GET /status - Check service status');
});
