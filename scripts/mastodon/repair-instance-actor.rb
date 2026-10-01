# frozen_string_literal: true

# Repair the Mastodon instance actor (Account::INSTANCE_ACTOR_ID).
#
# Mastodon signs every outgoing ActivityPub request "on_behalf_of
# Account.representative". That actor's uri/inbox_url/shared_inbox_url are only
# populated by before_create callbacks, so if the database was first created
# under a different LOCAL_DOMAIN they stay empty and every remote server rejects
# our signed fetches with HTTP 401. Outbound federation then silently fails:
# search resolves nothing and no activity is ever delivered.
#
# This is idempotent and safe to run after any domain change.
base = "https://#{ENV.fetch('LOCAL_DOMAIN')}"
actor = Account.find(Account::INSTANCE_ACTOR_ID)

expected = {
  username: 'mastodon.internal',
  domain: nil,
  uri: "#{base}/users/mastodon.internal",
  inbox_url: "#{base}/users/mastodon.internal/inbox",
  shared_inbox_url: "#{base}/inbox",
}

changes = expected.reject { |k, v| actor.public_send(k) == v }
if changes.empty?
  puts "instance actor already correct for #{base}"
else
  actor.update!(expected)
  puts "repaired instance actor for #{base}: #{changes.keys.join(', ')}"
end
actor.reload
puts "  uri=#{actor.uri}"
puts "  shared_inbox=#{actor.shared_inbox_url}"
