# create-300x3-accounts.rb - local-instance account bootstrap.
# Skips the email-MX reachability validation because this is a LOCAL instance
# with no SMTP (documented deviation). Sets passwords from env passed in.
bot_user  = ENV['BOT_EMAIL']
bot_pass  = ENV['BOT_PASSWORD']
bot_name  = ENV['BOT_HANDLE']
adm_user  = ENV['ADMIN_HANDLE']
adm_email = ENV['ADMIN_EMAIL']
adm_pass  = ENV['ADMIN_PASSWORD']

owner_role = UserRole.find_by(name: 'Owner') || UserRole.find_by(position: -100)

[[adm_user, adm_email, adm_pass, owner_role],
 [bot_name, bot_user,  bot_pass,  nil]].each do |username, email, password, role|
  next if Account.exists?(username: username)
  user = User.new(
    email: email,
    password: password,
    agreement: true,
    approved: true,
    confirmed_at: Time.now.utc,
    role: role.presence
  )
  user.build_account(username: username, display_name: username)
  user.save!(validate: false)
  user.account.update!(locked: false)
  puts "CREATED #{user.account.username} (#{user.email}) role=#{user.role&.name}"
end
puts 'DONE'
