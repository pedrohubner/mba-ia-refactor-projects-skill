function ts() {
    return new Date().toISOString();
}
module.exports = {
    info: (msg) => console.log(`[${ts()}] [INFO] ${msg}`),
    error: (msg) => console.error(`[${ts()}] [ERROR] ${msg}`),
};
