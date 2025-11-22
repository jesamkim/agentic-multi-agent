import { PdfConverter } from './dist/pdf-converter.js';

async function convert() {
    const converter = new PdfConverter();
    const result = await converter.convertToPdf({
        htmlPath: '/Workshop/sct-esg/reports/20251122_164243_삼성물산_탄소배출량.html',
        outputPath: '/Workshop/sct-esg/reports/20251122_164243_삼성물산_탄소배출량_test.pdf',
        scale: 0.8,
        printBackground: true,
        format: 'A4',
        marginTop: '15mm',
        marginBottom: '15mm',
        marginLeft: '15mm',
        marginRight: '15mm'
    });

    await converter.cleanup();

    if (result.success) {
        console.log('SUCCESS');
    } else {
        console.error('FAILED:', result.error);
        process.exit(1);
    }
}

convert().catch(err => {
    console.error('ERROR:', err.message);
    process.exit(1);
});
