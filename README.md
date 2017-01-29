# screentime

A set of resources necessary for supporting a new skill for Amazon's Echo platform.

##Build

1. zip -f AddRemoveScreenTime1.zip *.py
2. cd virtual-env/lib/python2.7/site-packages/
3. zip -f AddRemoveScreenTime1.zip *
4. aws lambda update-function-code --function-name AddTime --zip-file fileb://AddRemoveScreenTime1.zip

##Dependencies
1. boto3 (1.4.4)
2. botocore (1.5.7)
3. docutils (0.13.1)
4. futures (3.0.5)
5. isodate (0.5.4)
6. jmespath (0.9.1)
7. pip (9.0.1)
8. python-dateutil (2.6.0)
9. s3transfer (0.1.10)
10. setuptools (32.3.0)
11. six (1.10.0)
12. wheel (0.29.0)