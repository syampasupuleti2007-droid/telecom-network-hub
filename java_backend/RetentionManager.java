package java_backend;

import java.util.ArrayList;
import java.util.List;

public class RetentionManager {
    private List<String> flaggedSubscribers;

    public RetentionManager() {
        flaggedSubscribers = new ArrayList<>();
    }

    public void flagSubscriberForRetention(String subscriberId, double churnProb) {
        if (churnProb >= 0.65) {
            flaggedSubscribers.add(subscriberId);
            System.out.println("ALERT: Subscriber " + subscriberId + " flagged for retention outreach! Churn Risk: " + (churnProb * 100) + "%");
        }
    }

    public List<String> getFlaggedSubscribers() {
        return flaggedSubscribers;
    }
}