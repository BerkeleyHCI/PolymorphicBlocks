package org.edg;

import org.eclipse.elk.alg.layered.options.LayeredMetaDataProvider;
import org.eclipse.elk.alg.layered.options.LayeredOptions;
import org.eclipse.elk.core.RecursiveGraphLayoutEngine;
import org.eclipse.elk.core.data.LayoutMetaDataService;
import org.eclipse.elk.core.options.*;
import org.eclipse.elk.core.math.KVector;
import org.eclipse.elk.core.util.BasicProgressMonitor;
import org.eclipse.elk.graph.util.ElkGraphUtil;
import py4j.GatewayServer;
import org.eclipse.elk.graph.*;
import org.eclipse.elk.graph.json.*;

import java.util.Scanner;

public class Main {
    //
    // ElkGraphUtil graph construction API
    //
    public static ElkNode createGraph() {
        ElkNode root = ElkGraphUtil.createGraph();
        root.setIdentifier("root");
        root.setProperty(CoreOptions.ALGORITHM, "org.eclipse.elk.layered");
        root.setProperty(CoreOptions.HIERARCHY_HANDLING, HierarchyHandling.INCLUDE_CHILDREN);
        root.setProperty(LayeredOptions.HIERARCHY_HANDLING, HierarchyHandling.INCLUDE_CHILDREN);
        root.setProperty(LayeredOptions.THOROUGHNESS, 7);

        root.setProperty(CoreOptions.NODE_LABELS_PLACEMENT, NodeLabelPlacement.insideTopCenter());
        root.setProperty(CoreOptions.PORT_LABELS_PLACEMENT, PortLabelPlacement.INSIDE);
        root.setProperty(CoreOptions.PORT_LABELS_NEXT_TO_PORT_IF_POSSIBLE, true);
        root.setProperty(CoreOptions.NODE_SIZE_CONSTRAINTS, SizeConstraint.minimumSizeWithPorts());
        return root;
    }

    public static ElkNode createNode(ElkNode parent, String text) {
        return createNode(parent, text, "");
    }

    public static ElkNode createNode(ElkNode parent, String text, String id_suffix) {
        ElkNode node = ElkGraphUtil.createNode(parent);
        node.setProperty(CoreOptions.NODE_LABELS_PLACEMENT, NodeLabelPlacement.insideTopCenter());
        node.setProperty(CoreOptions.PORT_LABELS_PLACEMENT, PortLabelPlacement.INSIDE);
        node.setProperty(CoreOptions.PORT_LABELS_NEXT_TO_PORT_IF_POSSIBLE, true);
        node.setIdentifier(parent.getIdentifier() + "-" + text + id_suffix);
        ElkLabel label = createLabel(text, node, "label");
        return node;
    }

    public static void setMinSize(ElkNode node, int x, int y) {
        node.setProperty(CoreOptions.NODE_SIZE_CONSTRAINTS, SizeConstraint.minimumSizeWithPorts());
        node.setProperty(CoreOptions.NODE_SIZE_MINIMUM, new KVector(x, y));
    }

    public static ElkPort createPort(ElkNode parent, String text) {
        ElkPort port = ElkGraphUtil.createPort(parent);
        port.setIdentifier(parent.getIdentifier() + "-" + text);
        port.setDimensions(10, 10);  // TODO configurable dimensions
        createLabel(text, port, "label");
        return port;
    }

    public static ElkEdge createEdge(ElkNode parent, String relid) {
        ElkEdge edge = ElkGraphUtil.createEdge(parent);
        edge.setIdentifier(parent.getIdentifier() + "-" + relid);
        return edge;
    }

    public static ElkEdge createEdge(ElkNode parent, String relid, ElkConnectableShape source, ElkConnectableShape target) {
        ElkEdge edge = createEdge(parent, relid);
        edge.getSources().add(source);
        edge.getTargets().add(target);
        return edge;
    }

    public static ElkLabel createLabel(String text, ElkGraphElement parent, String relid) {
        ElkLabel label = ElkGraphUtil.createLabel(text, parent);
        label.setIdentifier(parent.getIdentifier() + "-" + relid);
        return label;
    }

    public static ElkNode layout(ElkNode graph) {
        RecursiveGraphLayoutEngine engine = new RecursiveGraphLayoutEngine();
        engine.layout(graph, new BasicProgressMonitor());
        return graph;
    }

    //
    // Import/Export operations
    //
    public static ElkNode elkFromJson(String json) {
        return ElkGraphJson.forGraph(json).toElk();
    }

    public static String jsonFromElk(ElkNode root, boolean omitLayout) {
        return ElkGraphJson.forGraph(root)
                .omitLayout(omitLayout)
                .omitZeroDimension(true)
                .omitZeroPositions(true)
                .shortLayoutOptionKeys(false)
                .prettyPrint(true)
                .toJson();
    }

    //
    // Boilerplate
    //
    public static void main(String[] args) {
        LayoutMetaDataService.getInstance().registerLayoutMetaDataProviders(
                new LayeredMetaDataProvider()
        );

        GatewayServer gatewayServer = new GatewayServer(new Main());
        gatewayServer.start();
        System.out.println("Gateway Server Started");

        Scanner s = new Scanner(System.in);
        s.nextLine();
        gatewayServer.shutdown();
        System.exit(0);
    }
}
