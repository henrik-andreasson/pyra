# todo

## via browser
* fix first page overview
* search
* make input safe for sorting lists

## via rest api
* when data is sent in with incomplete data it does not work very well
* improve audit log, id:s do not explain very well ...
* test the rest api
* create test scripts
* create test suite

## common

* environment list should be global ..
environment = SelectField(_l('Environment'), choices=[('dev', 'Development'),
                                                      ('tools', 'Tools'),
                                                      ('cicd', 'CI/CD'),
                                                      ('st', 'System Testing'),
                                                      ('at', 'Acceptance Testing'),
                                                      ('prod', 'Production'),
                                                      ]) #_
