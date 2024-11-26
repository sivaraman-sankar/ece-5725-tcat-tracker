import React from "react";
import { Stage, Layer, Line, Rect, Text } from "react-konva";
const POINTS_PER_LINE = 10;

const StopsViewerGraph = ({ numPoints = 30, stops = [], busLocation=[] }) => {
  const numLines = Math.ceil(numPoints / POINTS_PER_LINE);
  const splitIntoLines = (text) => {
    return text.split(' ').join('\n');
  }
  const getIsIncoming = (stop) => {
    return busLocation.some((location) => location.includes(stop));
  };

  const getStopColor = (stop) => {
    return getIsIncoming(stop) ? "blue": "red";
  }

  const calculateLinePoints = (lineIndex) => {
    const points = [];
    const screenWidth = window.innerWidth;
    const xSpacing = screenWidth / (POINTS_PER_LINE + 1);
    const yPosition = (window.innerHeight / (numLines + 1)) * (lineIndex + 1);

    for (let i = 0; i < POINTS_PER_LINE; i++) {
      const x = xSpacing * (i + 1);
      points.push({ x, y: yPosition });
    }
    return points;
  };

  // Calculate points for all lines
  const allLines = Array.from({ length: numLines }, (_, index) =>
    calculateLinePoints(index)
  );

  const createConnector = (startPoint, endPoint, isInverted = false) => {
    const deltaX = 0;
    const deltaY = 0;

    const controlPoint1 = {
      x: startPoint.x + (isInverted ? -deltaX : deltaY),
      y: startPoint.y + (isInverted ? deltaY : 50),
    };

    const controlPoint2 = {
      x: endPoint.x + (isInverted ? -deltaX : deltaY),
      y: endPoint.y + (isInverted ? -deltaY : -50),
    };

    return [
      startPoint.x, startPoint.y,
      controlPoint1.x, controlPoint1.y,
      controlPoint2.x, controlPoint2.y,
      endPoint.x, endPoint.y,
    ];
  };

  if(stops.length == 0) {
    return (
      <React.Fragment>
      </React.Fragment>
    )
  }
  return (
    <React.Fragment>
    <Stage width={window.innerWidth} height={window.innerHeight}>
      <Layer>
        {allLines.map((linePoints, lineIndex) => (
          <React.Fragment key={`line-${lineIndex}`}>
            {/* Draw the straight line */}
            <Line
              points={linePoints.flatMap(point => [point.x, point.y])}
              stroke="green"
              strokeWidth={4}
              lineCap="round"
              lineJoin="round"
            />

            {/* Draw points on the line */}
            {linePoints.map((point, pointIndex) => (
              <React.Fragment key={`point-${lineIndex}-${pointIndex}`}>
                <Rect
                  x={point.x - 5}
                  y={point.y - 10}
                  width={10}
                  height={20}
                  fill={getStopColor(stops[lineIndex+pointIndex])}
                  // rotation={Math.random() * 360}
                  shadowBlur={5}
                />
                <Text
                  x={point.x}
                  y={point.y}
                  text={splitIntoLines(`${stops[lineIndex + pointIndex]}`)} // Use \n for new lines
                  fontSize={10}
                  fill="black"
                  align="left"
                  width={100} // Must specify width for text wrapping
                  padding={5}
                  lineHeight={1.2} // Controls spacing between lines
                />
              </React.Fragment>

            ))}

            {/* Draw connectors between lines */}
            {lineIndex < numLines - 1 && (
              <>
                {/* For odd-numbered lines (0-based index), connect last points */}
                {lineIndex % 2 === 0 ? (
                  <Line
                    points={createConnector(
                      linePoints[linePoints.length - 1],
                      allLines[lineIndex + 1][allLines[lineIndex + 1].length - 1],
                      false
                    )}
                    stroke="green"
                    strokeWidth={2}
                  />
                ) :
                  /* For even-numbered lines, connect first points */
                  (
                    <Line
                      points={createConnector(
                        linePoints[0],
                        allLines[lineIndex + 1][0],
                        true
                      )}
                      stroke="green"
                      strokeWidth={2}
                    />
                  )}
              </>
            )}
          </React.Fragment>
        ))}
      </Layer>
    </Stage>
    </React.Fragment>
  );
};

export default StopsViewerGraph;