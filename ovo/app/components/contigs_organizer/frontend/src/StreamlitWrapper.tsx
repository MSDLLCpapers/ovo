import {
    StreamlitComponentBase,
    withStreamlitConnection,
    Streamlit
} from "streamlit-component-lib";
import React, { ReactNode } from "react";
import ContigsOrganizer from "./ContigsOrganizer";
import { StreamlitComponentValue } from "./types";

interface State {
    currentComponentState: StreamlitComponentValue | null;
}

class StreamlitWrapper extends StreamlitComponentBase<State> {

    constructor(props: any) {
        super(props);
        this.state = { currentComponentState: null };
        this.updateStreamlitComponentValue = this.updateStreamlitComponentValue.bind(this);
    }

    updateStreamlitComponentValue = (newValue: StreamlitComponentValue) => {
        this.setState(prevState => {
            if (prevState?.currentComponentState) {
                const prevValueString = JSON.stringify(prevState.currentComponentState);
                const newValueString = JSON.stringify(newValue);
                if (prevValueString !== newValueString) {
                    Streamlit.setComponentValue({
                        previous: prevState.currentComponentState,
                        current: newValue
                    });
                }
            }
            return {
                ...prevState,
                currentComponentState: newValue
            };
        });
    };


    public render = (): ReactNode => {
        const contigs: string = this.props.args["contigs"];
        const pdb: string = this.props.args["pdb"];
        const colors: Map<string, string> = new Map(Object.entries(JSON.parse(this.props.args["colors"])));
        const unindexedSegments: Set<string> = new Set(JSON.parse(this.props.args["unindexed_segments"] ?? "[]"));

        const hasContigs = contigs && contigs.trim() !== "";
        if (!hasContigs && unindexedSegments.size === 0) {
            return "No contigs provided.";
        }

        return (
            <ContigsOrganizer contigs={contigs ?? ""} pdb={pdb} colors={colors}
                unindexedSegments={unindexedSegments}
                updateStreamlitComponentValue={this.updateStreamlitComponentValue} />
        );
    };
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
export default withStreamlitConnection(StreamlitWrapper);
