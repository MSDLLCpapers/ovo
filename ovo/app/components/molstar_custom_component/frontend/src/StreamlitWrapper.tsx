import {
    StreamlitComponentBase,
    withStreamlitConnection,
    Streamlit
} from "streamlit-component-lib";
import React, { ReactNode } from "react";
import MolstarCustomComponent from "./MolstarCustomComponent";
import { ContigSegment, StreamlitComponentValue } from "./types";

interface State {
    highlightedContig: ContigSegment & { structureIdx: number; } | null;
    currentComponentState: StreamlitComponentValue | null;
    isFullscreen: boolean;
}

class StreamlitWrapper extends StreamlitComponentBase<State> {

    constructor(props: any) {
        super(props);
        this.state = { highlightedContig: null, currentComponentState: null, isFullscreen: false };

        this.setHighlightedContig = this.setHighlightedContig.bind(this);
        this.updateStreamlitComponentValue = this.updateStreamlitComponentValue.bind(this);
        this.handleFullscreenChange = this.handleFullscreenChange.bind(this);
    }

    componentDidMount() {
        document.addEventListener('fullscreenchange', this.handleFullscreenChange);
        document.addEventListener('webkitfullscreenchange', this.handleFullscreenChange);

        // Use a small delay to allow the DOM to fully render
        setTimeout(() => {
            Streamlit.setFrameHeight();
        }, 100);
    }

    componentWillUnmount() {
        document.removeEventListener('fullscreenchange', this.handleFullscreenChange);
        document.removeEventListener('webkitfullscreenchange', this.handleFullscreenChange);
    }

    handleFullscreenChange = () => {
        const isFullscreen = !!(
            document.fullscreenElement || (document as any).webkitFullscreenElement
        );

        this.setState({ isFullscreen });

        // notify Streamlit to resize after exiting fullscreen
        if (!isFullscreen) {
            setTimeout(() => {
                Streamlit.setFrameHeight();
            }, 100);
        }
    };

    setHighlightedContig = (newContig: ContigSegment, structureIdx: number) => {
        this.setState(prevState => {
            return {
                ...prevState,
                highlightedContig: {
                    ...newContig,
                    structureIdx: structureIdx
                }
            };
        });
    };

    updateStreamlitComponentValue = (newValue: StreamlitComponentValue) => {
        this.setState(prevState => {
            if (prevState?.currentComponentState) {
                const prevValueString = JSON.stringify(prevState.currentComponentState);
                const newValueString = JSON.stringify(newValue);
                if (prevValueString !== newValueString) {
                    Streamlit.setComponentValue(newValueString);
                }
            }
            return {
                ...prevState,
                currentComponentState: newValue
            };
        });
    };

    public render = (): ReactNode => {
        const structures = JSON.parse(this.props.args["structures"]);
        const key = this.props.args["key"];
        const divName = `molstar-wrapper-${key}`;
        const showControls = this.props.args["showControls"];
        const selectionMode = this.props.args["selectionMode"];
        const forceReload = this.props.args["forceReload"] ?? false;

        const requestedHeight = this.props.args["height"];
        const contigsHeight = 25; // for the contigs

        const originalWidth = this.props.args["width"];
        const effectiveWidth = this.state.isFullscreen ? "100%" : originalWidth;

        // parse all contigs for each of the structures
        const allContigsParsed: ContigSegment[][] = [];
        structures.forEach((s: any) => allContigsParsed.push(s["contigs"] ?? []));

        return (
            <>
                <div id={divName} style={{ height: requestedHeight, width: effectiveWidth }}>
                    <MolstarCustomComponent structures={structures} divName={divName} showControls={showControls}
                        contigs={allContigsParsed} highlightedContig={this.state.highlightedContig}
                        selectionMode={selectionMode} updateStreamlitComponentValue={this.updateStreamlitComponentValue}
                        forceReload={forceReload}
                    />
                </div>
                {!this.state.isFullscreen && allContigsParsed.map((parsedContigs, outerIdx) => {
                    if (parsedContigs.length > 0) return (
                        <div class="msp-layout-contig" style={{ color: "black", fontSize: "14px", cursor: "default" }} key={outerIdx}>
                            Segments: {parsedContigs.map((e, idx) => {
                                if (e.middle_label || e.start_label) {
                                    const contigDescription = e.middle_label ? `${e.middle_label} ` : `${e.start_label}-${e.end_label} `;
                                    return <span style={{ color: e.color }} onMouseOver={() => this.setHighlightedContig(e, outerIdx)} key={idx}>{contigDescription}</span>;
                                }
                                return <React.Fragment key={idx}></React.Fragment>;
                            })}
                        </div>);
                    return <React.Fragment key={outerIdx}></React.Fragment>;
                })}
            </>
        );
    };
}

// "withStreamlitConnection" is a wrapper function. It bootstraps the
// connection between your component and the Streamlit app, and handles
// passing arguments from Python -> Component.
export default withStreamlitConnection(StreamlitWrapper);
