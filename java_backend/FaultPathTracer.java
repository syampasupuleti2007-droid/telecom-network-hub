package java_backend;

import java.util.*;

public class FaultPathTracer {
    private Map<String, List<String>> networkGraph;

    public FaultPathTracer() {
        networkGraph = new HashMap<>();
        networkGraph.put("Tower_A", Arrays.asList("Substation_1"));
        networkGraph.put("Tower_B", Arrays.asList("Substation_1"));
        networkGraph.put("Tower_C", Arrays.asList("Tower_B"));
        networkGraph.put("Substation_1", Arrays.asList("Central_Hub"));
    }

    public List<String> tracePath(String startNode) {
        List<String> path = new ArrayList<>();
        String current = startNode;
        path.add(current);

        while (networkGraph.containsKey(current) && !networkGraph.get(current).isEmpty()) {
            current = networkGraph.get(current).get(0);
            path.add(current);
            if (current.equals("Central_Hub")) break;
        }
        return path;
    }

    public static void main(String[] args) {
        FaultPathTracer tracer = new FaultPathTracer();
        System.out.println("Path from Tower_A: " + tracer.tracePath("Tower_A"));
    }
}