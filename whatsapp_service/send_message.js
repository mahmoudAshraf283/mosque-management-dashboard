const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

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

// Generate QR code for authentication
client.on('qr', (qr) => {
    console.log('QR Code received. Scan this with WhatsApp:');
    qrcode.generate(qr, { small: true });
});

// Client is ready
client.on('ready', async () => {
    console.log('WhatsApp Client is ready!');
    
    // Get message details from command line arguments
    const phoneNumber = process.argv[2]; // e.g., "966501234567"
    const message = process.argv[3];
    
    if (!phoneNumber || !message) {
        console.error('Usage: node send_message.js <phone_number> <message>');
        process.exit(1);
    }
    
    try {
        // Format phone number (remove any non-digits and add @c.us)
        const formattedNumber = phoneNumber.replace(/\D/g, '') + '@c.us';
        
        // Send message
        await client.sendMessage(formattedNumber, message);
        console.log(`Message sent successfully to ${phoneNumber}`);
        
        // Exit after sending
        setTimeout(() => {
            process.exit(0);
        }, 2000);
    } catch (error) {
        console.error('Error sending message:', error);
        process.exit(1);
    }
});

client.on('authenticated', () => {
    console.log('WhatsApp authenticated successfully');
});

client.on('auth_failure', (msg) => {
    console.error('Authentication failed:', msg);
    process.exit(1);
});

client.on('disconnected', (reason) => {
    console.log('Client was disconnected:', reason);
});

// Initialize the client
client.initialize();
