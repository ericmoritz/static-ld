
Given /^I run the command "([^"]*)"$/ do |cmd|
  raise unless system(cmd)
end

Then /^the rendered files at "([^"]*)" should match the files at "([^"]*)"$/ do |out_dir, expected|
  raise unless system("diff '#{out_dir}' '#{expected}'")
end
