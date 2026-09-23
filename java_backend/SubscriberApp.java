package java_backend;

import java.util.HashMap;
import java.util.Map;

public class SubscriberApp {
    private Map<String, String> subscriberTowerMap;

    public SubscriberApp() {
        subscriberTowerMap = new HashMap<>();
        // Mock data initialization
        subscriberTowerMap.put("SUB001", "Tower_A");
        subscriberTowerMap.put("SUB002", "Tower_B");
        subscriberTowerMap.put("SUB003", "Tower_C");
    }

    public String getTowerForSubscriber(String subscriberId) {
        return subscriberTowerMap.getOrDefault(subscriberId, "Unknown Tower");
    }

    public static void main(String[] args) {
        SubscriberApp app = new SubscriberApp();
        System.out.println("Java Subscriber Management Initialized.");
        System.out.println("SUB001 connected to: " + app.getTowerForSubscriber("SUB001"));
    }
}