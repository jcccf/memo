require 'ruby-aws'
@mturk = Amazon::WebServices::MechanicalTurkRequester.new :Host => :Sandbox

# Use this line instead if you want the production website.
#@mturk = Amazon::WebServices::MechanicalTurkRequester.new :Host => :Production

def createNewHIT
  title = "Movie Quotes Survey"
  desc = "We want to study how well people remember movie quotes."
  keywords = "movie, survey"
  numAssignments = 10
  rewardAmount = 0.50 # 50 cents
  duration = 600 # 10 minutes
  
  # qualifications = {
  #   :QualificationTypeId => '2D5WYB49F9SS68SJWHFNVT5H5GNUQN',
  #   :Comparator => 'GreaterThan',
  #   :IntegerValue => '10'
  # }
  
  # Define the location of the externalized question (QuestionForm) file.
  rootDir = File.dirname $0
  questionFile = rootDir + "/external.xml"

  # Load the question (QuestionForm) file
  question = File.read( questionFile )
  
  result = @mturk.createHIT( :Title => title,
    :Description => desc,
    :MaxAssignments => numAssignments,
    :Reward => { :Amount => rewardAmount, :CurrencyCode => 'USD' },
    :AssignmentDurationInSeconds => duration,
    :Question => question,
    :Keywords => keywords )
    #:QualificationRequirement => qualifications )

  puts "Created HIT: #{result[:HITId]}"
  puts "HIT Location: #{getHITUrl( result[:HITTypeId] )}"
  return result
end

def getHITUrl( hitTypeId )
  if @mturk.host =~ /sandbox/
    "http://workersandbox.mturk.com/mturk/preview?groupId=#{hitTypeId}"   # Sandbox Url
  else
    "http://mturk.com/mturk/preview?groupId=#{hitTypeId}"   # Production Url
  end
end

def createQualification
  result = @mturk.createQualificationType(
    :Name => 'Movie Quotes Quiz 2',
    :Description => 'A description of this quizzical quiz',
    :Keywords => 'mbtz, mbtl',
    :RetryDelayInSeconds => 3000,
    :QualificationTypeStatus => 'Active',
    :Test => File.read('qualification_test.xml'),
    :AnswerKey => File.read('qualification_test_answers.xml'),
    :TestDurationInSeconds => 300
  )
  result[:QualificationTypeId] # Return QualificationTypeId for later use
end

createNewHIT

#puts createQualification

#puts @mturk.getAssignmentsForHIT(:HITId => '2IDP9746OQ1S1HLPL4Y081QKFFQM2L')