const fs = require('node:fs');
const vm = require('node:vm');
for (const file of ['index.html', 'admin.html', 'profile.html', 'login.html', 'checkin.html', 'reset_password.html', 'user_info.html', 'workspace.html', 'certificate.html']) {
    const source = fs.readFileSync(file, 'utf8');
    for (const [i, match] of [...source.matchAll(/<script\b[^>]*>([\s\S]*?)<\/script\s*>/gi)].entries()) {
        new vm.Script(match[1], { filename: `${file}:${i}` });
    }
    console.log(`${file}: syntax OK`);
}
