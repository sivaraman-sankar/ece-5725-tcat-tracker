import React, { useState, useEffect } from "react";
import { Stage, Layer, Line, Rect, Text } from "react-konva";
const POINTS_PER_LINE = 5;

const StopsViewerGraph = ({ numPoints = 30, stops = [], busLocation = [] }) => {
  const [dimensions, setDimensions] = useState({
    width: window.innerWidth * 0.9, // Use 90% of viewport width
    height: window.innerHeight * 0.6 // Use 60% of viewport height
  });

  useEffect(() => {
    const handleResize = () => {
      setDimensions({
        width: window.innerWidth * 0.9,
        height: window.innerHeight * 0.6
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const numLines = Math.ceil(numPoints / POINTS_PER_LINE);
  
  const splitIntoLines = (text) => {
    return text.split(' ').join('\n');
  }

  const getIsIncoming = (stop) => {
    return busLocation.some((location) => location.includes(stop));
  };

  const getStopColor = (stops, lineIndex, pointIndex) => {
    const stop = getStop(stops, lineIndex, pointIndex);
    if(!!!stop) return 'black';

    return stop['is_incoming'] ? "blue" : "red";
  }

  const getStop = (stops, lineIndex, pointIndex) => {
    if (!stops || stops.length === 0) return 'N/A';

    const start = lineIndex * POINTS_PER_LINE;
    const end = start + POINTS_PER_LINE - 1;

    // Determine the correct index based on whether the lineIndex is odd or even
    const index = (lineIndex % 2 === 0) 
        ? start + pointIndex // Even lineIndex: normal order
        : end - pointIndex;  // Odd lineIndex: reverse order

    const stop = stops[index];
    return stop;
  }


  const getStopName = (stops, lineIndex, pointIndex) => {
    const stop = getStop(stops, lineIndex, pointIndex);
    if (!stop) return 'N/A';
    return stop['stop_name'];
};

  const calculateLinePoints = (lineIndex) => {
    const points = [];
    const xSpacing = dimensions.width / (POINTS_PER_LINE + 1);
    // Reduce vertical spacing between lines
    const yPosition = (dimensions.height / (numLines + 0.5)) * (lineIndex + 0.5);

    for (let i = 0; i < POINTS_PER_LINE; i++) {
      const x = xSpacing * (i + 1);
      points.push({ x, y: yPosition });
    }
    return points;
  };

  const allLines = Array.from({ length: numLines }, (_, index) =>
    calculateLinePoints(index)
  );

  const createConnector = (startPoint, endPoint, isInverted = false) => {
    return [
      startPoint.x, startPoint.y,
      endPoint.x, endPoint.y,
    ];
  };

  const getReverse = (linePoints) => {
    const reversedLinePoints = linePoints.slice().reverse();
    return reversedLinePoints;
  }

  if(stops.length === 0) {
    return null;
  }

  return (
    <Stage width={dimensions.width} height={dimensions.height}>
      <Layer>
        {allLines.map((linePoints, lineIndex) => (
          <React.Fragment key={`line-${lineIndex}`}>
            {lineIndex % 2 == 1 ? <Line
              points={linePoints.flatMap(point => [point.x, point.y])}
              stroke="green"
              strokeWidth={0.5}
              lineCap="round"
              lineJoin="round"
            /> :
            <Line
              points={(getReverse(linePoints)).flatMap(point => [point.x, point.y])}
              stroke="green"
              strokeWidth={0.5}
              lineCap="round"
              lineJoin="round"
            />  }

            {linePoints.map((point, pointIndex) => (
              <React.Fragment key={`point-${lineIndex}-${pointIndex}`}>
                <Rect
                  x={point.x - 5}
                  y={point.y - 10}
                  width={10}
                  height={20}
                  fill={getStopColor(stops, lineIndex, pointIndex)}
                  shadowBlur={3}
                />
                <Text
                  x={point.x + 10}
                  y={point.y - 15}
                  text={splitIntoLines(`${getStopName(stops, lineIndex, pointIndex)}`)}
                  fontSize={12}
                  fill="black"
                  align="left"
                  width={80}
                  padding={2}
                  lineHeight={1.1}
                />
              </React.Fragment>
            ))}

            {lineIndex < numLines - 1 && (
              <Line
                points={createConnector(
                  lineIndex % 2 === 0 
                    ? linePoints[linePoints.length - 1]
                    : linePoints[0],
                  lineIndex % 2 === 0
                    ? allLines[lineIndex + 1][allLines[lineIndex + 1].length - 1]
                    : allLines[lineIndex + 1][0],
                  lineIndex % 2 !== 0
                )}
                stroke="green"
                strokeWidth={0.5}
              />
            )}
          </React.Fragment>
        ))}
      </Layer>
    </Stage>
  );
};

export default StopsViewerGraph;