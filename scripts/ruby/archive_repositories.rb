
require 'github_api'
require 'date'
require 'json'

puts 'You can obtain your access token from: https://github.com/settings/applications#personal-access-tokens'
puts 'Your Github.com access token:'

GITHUB_PERSONAL_ACCESS_TOKEN = 'ADMIN_GITHUB_TOKEN'

puts 'Your Github.com organisation:'
github_org = 'ministryofjustice'

puts 'Inactive for number of days in the past:'
number_of_days = 1095

older_than_date = Date.today - number_of_days

github = Github.new auto_pagination: true, oauth_token: GITHUB_PERSONAL_ACCESS_TOKEN
repos = github.repos.list org: github_org

limit_to_older_repos = repos.reject { |repo| Date.parse(repo.pushed_at) > older_than_date }
sorted_repos = limit_to_older_repos.sort_by { |repo| repo.pushed_at }


out_file = File.new("out.txt", "w")

SEPARATOR = ','

unless sorted_repos.empty?
  puts "Repository#{SEPARATOR}Last pushed at#{SEPARATOR}Clone from"
end

sorted_repos.each do |repo|
  if "#{repo.archived}" == 'false'
    # puts "repos/ministryofjustice/#{repo.name}"
    out_file.puts("repos/ministryofjustice/#{repo.name}")
  end
end
out_file.close
system 'cat out.txt | xargs -P8 -L1 hub api -X PATCH -F archived=true'
File.delete(out_file)
