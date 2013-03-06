


contentApi <- scan("out_CONTENT-API")
discussion <- scan("out_DISCUSSION")
opta <- scan("out_OPTA")
zeitgeist <- scan("out_ZEITGEIST")

png("content-api.png")
hist(contentApi, main="Histogram of Content API requests", xlab="% of request time")
dev.off()

png("discussion.png")
hist(discussion, main="Histogram of Discussion requests", xlab="% of request time")
dev.off()

png("opta.png")
hist(opta, main="Histogram of Opta requests", xlab="% of request time")
dev.off()

png("zeitgeist.png")
hist(zeitgeist, main="Histogram of Zeitgeist responses", xlab="% of req")
dev.off()
