# update-300x3-emails.rb - point both accounts at the operator posteo mailbox.
# Bot uses plus-addressing (users.email is UNIQUE at the schema level).
admin = User.find_by(email: 'admin@300x3.com')
bot   = User.find_by(email: 'bot@300x3.com')
abort 'admin user not found' unless admin
abort 'bot user not found' unless bot
admin.update!(email: ENV['ADMIN_EMAIL'])
bot.update!(email: ENV['BOT_EMAIL'])
puts "admin -> #{admin.reload.email} (#{admin.account.username})"
puts "bot   -> #{bot.reload.email} (#{bot.account.username})"
puts 'EMAILS-UPDATED'
