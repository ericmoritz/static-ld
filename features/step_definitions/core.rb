Given(/^I have an empty directory at "(.*?)"$/) do |output_dir|
  raise unless system("rm -rf '#{output_dir}'")
  raise unless system("mkdir -p '#{output_dir}'")
end


When /^I run the command "([^"]*)"$/ do |cmd|
  raise unless system(cmd)
end

Then /^the rendered files at "([^"]*)" should match the files at "([^"]*)"$/ do |out_dir, expected|
  raise unless system("diff -r '#{out_dir}' '#{expected}'")
end
